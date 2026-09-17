#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Object = UnityEngine.Object;

public sealed class AwfulModelViewerWindow : EditorWindow
{
    private const string StudioRoot = "Assets/AwfulViewer/Generated/Models/Studio";
    private const string SiteRoot = "Assets/AwfulViewer/Generated/Models/Site";
    private const string LogoRoot = "Assets/AwfulViewer/Generated/Logos";
    private const string CatalogPath = "Assets/AwfulViewer/Generated/catalog.json";

    [Serializable]
    private sealed class LogoCatalog
    {
        public LogoItem[] logos = Array.Empty<LogoItem>();
    }

    [Serializable]
    private sealed class LogoItem
    {
        public string file = "";
        public string name = "";
    }

    private sealed class Entry
    {
        public string Path;
        public string Label;
        public string Kind;
        public Object Asset;
    }

    private readonly List<Entry> entries = new();
    private readonly Dictionary<string, string> logoNames = new(StringComparer.OrdinalIgnoreCase);
    private Vector2 scroll;
    private string search = "";
    private int category;
    private Entry selection;
    private UnityEditor.Editor previewEditor;

    [MenuItem("AWFUL/Model Viewer %#m")]
    internal static void OpenWindow()
    {
        var window = GetWindow<AwfulModelViewerWindow>("AWFUL Models");
        window.minSize = new Vector2(860, 520);
        window.Show();
    }

    [MenuItem("AWFUL/Sync Model Assets")]
    private static void SyncAssetsMenu()
    {
        RunSync();
        AssetDatabase.Refresh();
        if (HasOpenInstances<AwfulModelViewerWindow>())
            GetWindow<AwfulModelViewerWindow>().RefreshCatalog();
    }

    private void OnEnable()
    {
        RefreshCatalog();
    }

    private void OnDisable()
    {
        DestroyPreviewEditor();
    }

    private void OnGUI()
    {
        DrawToolbar();
        EditorGUILayout.BeginHorizontal();
        DrawSidebar();
        DrawPreview();
        EditorGUILayout.EndHorizontal();
    }

    private void DrawToolbar()
    {
        EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
        category = GUILayout.Toolbar(
            category,
            new[] { "All", "Studio", "Site", "Logos" },
            EditorStyles.toolbarButton,
            GUILayout.Width(300));
        GUILayout.Space(8);
        search = GUILayout.TextField(search, GUI.skin.FindStyle("ToolbarSearchTextField"), GUILayout.MinWidth(180));
        GUILayout.FlexibleSpace();
        if (GUILayout.Button("Refresh", EditorStyles.toolbarButton))
            RefreshCatalog();
        if (GUILayout.Button("Sync", EditorStyles.toolbarButton))
        {
            RunSync();
            AssetDatabase.Refresh();
            RefreshCatalog();
        }
        EditorGUILayout.EndHorizontal();
    }

    private void DrawSidebar()
    {
        EditorGUILayout.BeginVertical(GUILayout.Width(280));
        var visible = FilteredEntries().ToList();
        EditorGUILayout.LabelField($"Assets: {visible.Count}", EditorStyles.miniBoldLabel);
        scroll = EditorGUILayout.BeginScrollView(scroll);
        foreach (var entry in visible)
        {
            bool selected = selection == entry;
            var style = selected ? EditorStyles.helpBox : EditorStyles.label;
            if (GUILayout.Button($"{entry.Label}\n{entry.Kind}", style, GUILayout.Height(42)))
                SelectEntry(entry);
        }
        EditorGUILayout.EndScrollView();
        EditorGUILayout.EndVertical();
    }

    private IEnumerable<Entry> FilteredEntries()
    {
        string kind = category switch
        {
            1 => "Studio",
            2 => "Site",
            3 => "Logo",
            _ => null,
        };
        return entries.Where(entry =>
            (kind == null || entry.Kind == kind) &&
            (string.IsNullOrWhiteSpace(search) ||
             entry.Label.Contains(search, StringComparison.OrdinalIgnoreCase)));
    }

    private void DrawPreview()
    {
        EditorGUILayout.BeginVertical();
        if (selection == null)
        {
            EditorGUILayout.HelpBox("Choose a model or logo from the catalog.", MessageType.Info);
            EditorGUILayout.EndVertical();
            return;
        }

        EditorGUILayout.BeginHorizontal();
        EditorGUILayout.LabelField(selection.Label, EditorStyles.boldLabel);
        GUILayout.FlexibleSpace();
        if (GUILayout.Button("Ping", GUILayout.Width(56)))
            EditorGUIUtility.PingObject(selection.Asset);
        if (GUILayout.Button("Reveal", GUILayout.Width(64)))
            EditorUtility.RevealInFinder(Path.GetFullPath(selection.Path));
        EditorGUILayout.EndHorizontal();
        EditorGUILayout.LabelField(selection.Path, EditorStyles.miniLabel);

        Rect rect = GUILayoutUtility.GetRect(
            200, 200,
            GUILayout.ExpandWidth(true),
            GUILayout.ExpandHeight(true));
        EditorGUI.DrawRect(rect, new Color(0.08f, 0.08f, 0.08f, 1f));

        if (previewEditor != null && previewEditor.HasPreviewGUI())
            previewEditor.OnInteractivePreviewGUI(rect, GUIStyle.none);
        else
            DrawFallbackPreview(rect);
        EditorGUILayout.EndVertical();
    }

    private void DrawFallbackPreview(Rect rect)
    {
        Texture2D preview = AssetPreview.GetAssetPreview(selection.Asset);
        if (preview == null)
            preview = AssetPreview.GetMiniThumbnail(selection.Asset);
        if (preview != null)
            GUI.DrawTexture(rect, preview, ScaleMode.ScaleToFit, true);
    }

    private void SelectEntry(Entry entry)
    {
        selection = entry;
        DestroyPreviewEditor();
        previewEditor = UnityEditor.Editor.CreateEditor(entry.Asset);
        Repaint();
    }

    private void DestroyPreviewEditor()
    {
        if (previewEditor == null)
            return;
        DestroyImmediate(previewEditor);
        previewEditor = null;
    }

    private void RefreshCatalog()
    {
        string previousPath = selection?.Path;
        entries.Clear();
        LoadLogoNames();
        AddModels(StudioRoot, "Studio");
        AddModels(SiteRoot, "Site");
        AddLogos();
        selection = entries.FirstOrDefault(entry => entry.Path == previousPath);
        if (selection != null)
            SelectEntry(selection);
        Repaint();
    }

    private void AddModels(string root, string kind)
    {
        foreach (string guid in AssetDatabase.FindAssets("t:GameObject", new[] { root }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (!path.EndsWith(".fbx", StringComparison.OrdinalIgnoreCase))
                continue;
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (asset == null)
                continue;
            string rawStem = Path.GetFileNameWithoutExtension(path);
            string stem = kind == "Site"
                ? rawStem.Split(new[] { "__" }, StringSplitOptions.None).Last()
                : rawStem;
            entries.Add(new Entry
            {
                Path = path,
                Label = ObjectNames.NicifyVariableName(stem),
                Kind = kind,
                Asset = asset,
            });
        }
    }

    private void LoadLogoNames()
    {
        logoNames.Clear();
        var asset = AssetDatabase.LoadAssetAtPath<TextAsset>(CatalogPath);
        if (asset == null)
            return;
        var catalog = JsonUtility.FromJson<LogoCatalog>(asset.text);
        if (catalog?.logos == null)
            return;
        foreach (var item in catalog.logos)
        {
            if (!string.IsNullOrWhiteSpace(item.file) && !string.IsNullOrWhiteSpace(item.name))
                logoNames[item.file] = item.name;
        }
    }

    private void AddLogos()
    {
        foreach (string guid in AssetDatabase.FindAssets("t:Texture2D", new[] { LogoRoot }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (!path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                continue;
            var asset = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (asset == null)
                continue;
            entries.Add(new Entry
            {
                Path = path,
                Label = LogoLabel(path),
                Kind = "Logo",
                Asset = asset,
            });
        }
        entries.Sort((a, b) => string.Compare(a.Label, b.Label, StringComparison.OrdinalIgnoreCase));
    }

    private string LogoLabel(string path)
    {
        string stem = Path.GetFileNameWithoutExtension(path);
        string fileId = stem.Replace("client-logo-", "", StringComparison.OrdinalIgnoreCase);
        return logoNames.TryGetValue(fileId, out string name)
            ? name
            : ObjectNames.NicifyVariableName(stem);
    }

    private static void RunSync()
    {
        string projectRoot = Directory.GetParent(Application.dataPath)?.FullName
            ?? throw new InvalidOperationException("Unity project root not found");
        string script = Path.Combine(projectRoot, "Tools", "sync-assets.ps1");
        if (!File.Exists(script))
            throw new FileNotFoundException("AWFUL sync script not found", script);

        var startInfo = new ProcessStartInfo
        {
            FileName = "pwsh",
            Arguments = $"-NoProfile -ExecutionPolicy Bypass -File \"{script}\"",
            WorkingDirectory = projectRoot,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        EditorUtility.DisplayProgressBar("AWFUL Model Viewer", "Syncing Blender and website assets...", 0.5f);
        try
        {
            using Process process = Process.Start(startInfo)
                ?? throw new InvalidOperationException("Failed to start PowerShell sync process");
            process.WaitForExit();
            if (process.ExitCode != 0)
                throw new InvalidOperationException($"Asset sync failed with exit code {process.ExitCode}");
        }
        finally
        {
            EditorUtility.ClearProgressBar();
        }
    }
}
#endif
