# iPhone v30 texture derivation

The official `ios26_home_screen_1206x2622.png` remains unchanged. Its provenance is recorded by the generator: Apple Support iPhone User Guide, iOS 26 Home Screen.

`ios26_home_screen_clean_1206x2622.png` is a 1206 × 2622 RGB derivative. OpenAI imagegen reconstructed wallpaper beneath the top-center black pill. Only pixels in the original pill mask, with a six-pixel dilation and two-pixel feather, were composited into the original. Artwork outside that region is pixel-identical. The physical Dynamic Island and optics remain model geometry; Apple's hardware keepout datum is independent of the visible silhouette datum.

Inpaint prompt: remove only the black top-center Dynamic Island pill, reconstruct continuous blue/cyan wallpaper, preserve all icons, text, status indicators, dimensions and composition.

`flash_diffuser_v30.png` is a 512 × 512 sRGB image synthesized with OpenAI imagegen: neutral ivory frosted diffuser, concentric Fresnel rings, fine microlens grid and faint warm/cool LED quadrants, even diffuse illumination, no phone body or exterior metallic rim. It is an illustrative diffuser approximation, not a measured photograph of iPhone flash hardware. The physical disk and ring dimensions still follow the existing device drawing. UVs project the image across the local XY cylinder face; the packed image is connected to MAT_FLASH base color and embedded in both GLB deliveries.

Both delivered images participate in the canonical source fingerprint. No external texture requests are needed at runtime.
