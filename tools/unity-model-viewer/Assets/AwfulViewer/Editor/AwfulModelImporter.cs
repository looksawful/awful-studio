#if UNITY_EDITOR
using UnityEditor;

public sealed class AwfulModelImporter : AssetPostprocessor
{
    private const string StudioRoot =
        "Assets/AwfulViewer/Generated/Models/Studio/";

    private void OnPreprocessModel()
    {
        if (!assetPath.StartsWith(StudioRoot,
                System.StringComparison.OrdinalIgnoreCase))
            return;

        if (assetImporter is not ModelImporter importer)
            return;

        importer.bakeAxisConversion = true;
        importer.importAnimation = false;
        importer.importCameras = false;
        importer.importLights = false;
    }
}
#endif
