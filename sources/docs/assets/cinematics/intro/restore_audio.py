"""Optional: prepare locally owned original audio; it is never bundled in public sources."""
from pathlib import Path
import argparse,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--legacy-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();source=args.legacy_root/'_INTRO/INTRO.GDV';assert source.is_file();assert not args.output.exists(),'Refusing to overwrite an existing soundtrack.'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(source),'-map','0:a:0','-vn','-t',str(826/24),'-c:a','aac','-b:a','128k',str(args.output)],check=True);print('LOCAL_SOUNDTRACK_PREPARED')
