"""Strict geometry/render coverage with a small stochastic edge-sampling budget."""
from PIL import ImageChops,ImageFilter


def compare_coverage(native,imported):
    a=native.getchannel('A');b=imported.getchannel('A')
    delta=ImageChops.difference(a,b)
    binary=lambda alpha:alpha.point(lambda value:255 if value>=128 else 0)
    aa,bb=binary(a),binary(b)
    different=ImageChops.difference(aa,bb)
    # A changed binary pixel must lie in both boundary bands, or remain
    # partially covered in both views near the threshold (a subpixel slot
    # can disappear from the binary mask when one of 24 samples changes).
    edge=lambda mask:ImageChops.difference(mask.filter(ImageFilter.MaxFilter(3)),mask.filter(ImageFilter.MinFilter(3)))
    boundary=ImageChops.multiply(edge(aa),edge(bb))
    near_threshold=lambda alpha:alpha.point(lambda value:255 if 96<=value<=160 else 0)
    partial=ImageChops.multiply(near_threshold(a),near_threshold(b))
    partial=ImageChops.multiply(partial,delta.point(lambda value:255 if value<=22 else 0))
    allowed=ImageChops.lighter(boundary,partial)
    assert ImageChops.subtract(different,allowed).getbbox() is None,'Changed interior or displaced silhouette'
    count=sum(value!=0 for value in delta.tobytes())
    binary_count=sum(value!=0 for value in different.tobytes())
    coverage_error=sum(delta.tobytes())/255
    # 24-sample Cycles coverage changes in steps of roughly 11/255. Tiny
    # native/glTF float differences can flip isolated edge samples. Keep
    # total error below two fully covered pixels in a 512x512 render.
    assert count<=64 and binary_count<=8 and coverage_error<=2,(count,binary_count,coverage_error)
    return dict(alpha_maximum=delta.getextrema()[1],alpha_differing_pixels=count,
                binary_silhouette_differing_pixels=binary_count,alpha_coverage_error_pixels=coverage_error,
                boundary_band_pixels=1,coverage_budget_pixels=2)
