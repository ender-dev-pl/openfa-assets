using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Xna.Framework;
using OpenFA.Client;
using OpenFA.Core.Modding;

if (args.Length != 2) throw new ArgumentException("Usage: ConstructionPreview sequence.json output-directory");
using var game = new ConstructionPreviewGame(args[0], args[1]);
game.Run();

// The host selects an authored asset sequence. All model drawing, PBR,
// shadows and AO execute in the actual OpenFA.Client MonoGame renderer.
internal sealed class ConstructionPreviewGame : Game
{
    private readonly JsonDocument plan;
    private readonly string output;
    private readonly string archive;
    private readonly Matrix camera;
    private readonly float scale;
    private readonly int size;
    private MonoGameSurfaceModelRenderer? renderer;

    public ConstructionPreviewGame(string path, string output)
    {
        this.output = Path.GetFullPath(output);
        Directory.CreateDirectory(this.output);
        plan = JsonDocument.Parse(File.ReadAllBytes(path));
        var root = plan.RootElement;
        archive = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(Path.GetFullPath(path))!, root.GetProperty("archive").GetString()!));
        var v = root.GetProperty("camera_matrix").EnumerateArray().SelectMany(row => row.EnumerateArray().Select(n => n.GetSingle())).ToArray();
        camera = Matrix.Transpose(new Matrix(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12], v[13], v[14], v[15]));
        scale = root.GetProperty("ortho_scale").GetSingle();
        size = root.GetProperty("resolution").GetInt32();
        _ = new GraphicsDeviceManager(this)
        {
            PreferredBackBufferWidth = size,
            PreferredBackBufferHeight = size,
            SynchronizeWithVerticalRetrace = false,
        };
        IsFixedTimeStep = false;
        IsMouseVisible = false;
        Window.Title = "OpenFA construction asset studio";
    }

    protected override void LoadContent() => renderer = new(GraphicsDevice, archive, BuildingAnimationPresentationDefinition.Empty);

    protected override void Draw(GameTime gameTime)
    {
        var frames = new List<object>();
        foreach (var item in plan.RootElement.GetProperty("frames").EnumerateArray())
        {
            var id = item.GetProperty("id").GetString()!;
            var path = Path.Combine(output, item.GetProperty("image").GetString()!);
            var texture = renderer!.RenderStudioProof(id, camera, scale, size, true, true);
            var pixels = new Color[size * size];
            texture.GetData(pixels);
            if (pixels.Count(p => p.A > 240) < size * size / 30)
                throw new InvalidDataException($"No visible studio frame: {id}");
            MonoGameSurfaceModelRenderer.WriteProofTexture(texture, path);
            frames.Add(new { id, image = Path.GetFileName(path), sha256 = Hash(path) });
        }
        var assemblies = new[] { typeof(MonoGameSurfaceModelRenderer).Assembly, typeof(BuildingAnimationPresentationDefinition).Assembly, typeof(Game).Assembly };
        var evidence = new
        {
            renderer = typeof(MonoGameSurfaceModelRenderer).FullName,
            method = "RenderStudioProof",
            lighting = "WorldLightingRig.Studio; PBR + shadows + AO",
            gameplayIntegration = false,
            graphicsAdapter = GraphicsDevice.Adapter.Description,
            graphicsProfile = GraphicsDevice.GraphicsProfile.ToString(),
            planSha256 = Hash(planPath()),
            archiveSha256 = Hash(archive),
            assemblies = assemblies.Select(a => new
            {
                name = a.GetName().Name,
                informationalVersion = a.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion,
                sha256 = Hash(a.Location),
            }),
            frames,
        };
        File.WriteAllText(Path.Combine(output, "runtime-evidence.json"), JsonSerializer.Serialize(evidence, new JsonSerializerOptions { WriteIndented = true }));
        Exit();

        string planPath() => Environment.GetCommandLineArgs()[1];
    }

    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();

    protected override void UnloadContent()
    {
        renderer?.Dispose();
        plan.Dispose();
    }
}
