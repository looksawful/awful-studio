#if UNITY_EDITOR
using UnityEditor;

[InitializeOnLoad]
internal static class AwfulViewerBootstrap
{
    private const string SessionKey = "AwfulViewer.OpenedThisSession.v2";

    static AwfulViewerBootstrap()
    {
        EditorApplication.delayCall += OpenOnce;
    }

    private static void OpenOnce()
    {
        if (SessionState.GetBool(SessionKey, false))
            return;

        SessionState.SetBool(SessionKey, true);
        AwfulModelViewerWindow.OpenWindow();
    }
}
#endif
