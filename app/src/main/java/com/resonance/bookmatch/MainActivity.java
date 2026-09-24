package com.resonance.bookmatch;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.graphics.Color;
import android.view.View;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {
    private static final int WRITE_REQUEST = 1001;
    private WebView webView;
    private String pendingJson;
    private String pendingFilename;
    private static final String PROFILE_PREFS = "resonance.profile";
    private static final String PROFILE_KEY = "json";

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(245,243,239));
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        webView.addJavascriptInterface(new AndroidBridge(), "Android");
        webView.setWebViewClient(new WebViewClient());
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.loadUrl("file:///android_asset/index.html");
        setContentView(webView);
    }

    private void saveToDownloads(String json, String filename) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
                values.put(MediaStore.Downloads.MIME_TYPE, "application/json");
                values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new Exception("Не вдалося створити файл");
                try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                    if (out == null) throw new Exception("Не вдалося відкрити файл");
                    out.write(json.getBytes(StandardCharsets.UTF_8));
                }
                notifySaved("Збережено в Downloads: " + filename);
            } else {
                File dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                if (!dir.exists() && !dir.mkdirs()) throw new Exception("Не вдалося створити Downloads");
                File file = new File(dir, filename);
                try (FileOutputStream out = new FileOutputStream(file)) {
                    out.write(json.getBytes(StandardCharsets.UTF_8));
                }
                notifySaved("Збережено в Downloads: " + filename);
            }
        } catch (Exception e) {
            Toast.makeText(this, "Не вдалося зберегти JSON: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void notifySaved(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
        String js = "window.onJsonSaved && window.onJsonSaved(" + quote(message) + ");";
        webView.post(() -> webView.evaluateJavascript(js, null));
    }

    private static String quote(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    public class AndroidBridge {
        @JavascriptInterface
        public String getProfile() {
            return getSharedPreferences(PROFILE_PREFS, MODE_PRIVATE).getString(PROFILE_KEY, "");
        }

        @JavascriptInterface
        public void saveProfile(String raw) {
            getSharedPreferences(PROFILE_PREFS, MODE_PRIVATE).edit().putString(PROFILE_KEY, raw).apply();
        }

        @JavascriptInterface
        public void saveJson(String json, String filename) {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q && checkSelfPermission("android.permission.WRITE_EXTERNAL_STORAGE") != PackageManager.PERMISSION_GRANTED) {
                pendingJson = json;
                pendingFilename = filename;
                requestPermissions(new String[]{"android.permission.WRITE_EXTERNAL_STORAGE"}, WRITE_REQUEST);
                return;
            }
            saveToDownloads(json, filename);
        }
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == WRITE_REQUEST) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                saveToDownloads(pendingJson, pendingFilename);
            } else {
                Toast.makeText(this, "Потрібен дозвіл на збереження файлу в Downloads", Toast.LENGTH_LONG).show();
            }
            pendingJson = null;
            pendingFilename = null;
        }
    }

    @Override public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack(); else super.onBackPressed();
    }
}
