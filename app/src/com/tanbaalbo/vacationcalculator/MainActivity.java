package com.tanbaalbo.vacationcalculator;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * 선원 유급휴가 계산기 앱.
 * 계산기(assets/index.html)를 WebView에 띄우고, 자바스크립트에 "Android" 다리를 넣어 준다.
 *  - loadData/saveData : 받아 둔 자료(임금표·공휴일)를 앱 내부 파일에 저장/읽기
 *  - bundledData       : 앱에 같이 넣은 assets/data.json
 *  - isOnline          : 인터넷 연결 여부
 *  - fetchData         : GitHub의 data.json을 받아 window.onDataFetched(글) / window.onDataFetchFailed(이유)로 돌려줌
 */
public class MainActivity extends Activity {
    static final String DATA_URL = "https://raw.githubusercontent.com/tanbaalbo/vacation_calculator/main/data.json";
    static final String STORE_FILE = "data_store.json";

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);      // 입력값 기억(localStorage)
        s.setAllowFileAccess(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        web.addJavascriptInterface(new Bridge(), "Android");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // 계산기 안의 바깥 링크는 휴대폰 브라우저로 연다
                if (url != null && (url.startsWith("http://") || url.startsWith("https://"))) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception e) { }
                    return true;
                }
                return false;
            }
        });
        setContentView(web);
        web.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onDestroy() {
        if (web != null) web.destroy();
        super.onDestroy();
    }

    class Bridge {
        @JavascriptInterface
        public String loadData() {
            return readFile(new File(getFilesDir(), STORE_FILE));
        }

        @JavascriptInterface
        public void saveData(String json) {
            writeFile(new File(getFilesDir(), STORE_FILE), json == null ? "" : json);
        }

        @JavascriptInterface
        public String bundledData() {
            try {
                InputStream in = getAssets().open("data.json");
                try { return readStream(in); } finally { in.close(); }
            } catch (Exception e) { return ""; }
        }

        @JavascriptInterface
        public boolean isOnline() {
            try {
                ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
                NetworkInfo ni = cm == null ? null : cm.getActiveNetworkInfo();
                return ni != null && ni.isConnected();
            } catch (Exception e) { return true; }
        }

        @JavascriptInterface
        public String appVersion() {
            try {
                PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
                return pi.versionName;
            } catch (Exception e) { return ""; }
        }

        @JavascriptInterface
        public void fetchData() {
            new Thread(new Runnable() {
                public void run() {
                    String text = null, err = "unknown";
                    HttpURLConnection c = null;
                    try {
                        c = (HttpURLConnection) new URL(DATA_URL).openConnection();
                        c.setConnectTimeout(10000);
                        c.setReadTimeout(15000);
                        c.setUseCaches(false);
                        c.setRequestProperty("Cache-Control", "no-cache");
                        int code = c.getResponseCode();
                        if (code == 200) text = readStream(c.getInputStream());
                        else err = "HTTP " + code;
                    } catch (Exception e) {
                        err = e.getClass().getSimpleName() + (e.getMessage() != null ? ": " + e.getMessage() : "");
                    } finally {
                        if (c != null) c.disconnect();
                    }
                    final String js = text != null
                        ? "window.onDataFetched(" + JSONObject.quote(text) + ")"
                        : "window.onDataFetchFailed(" + JSONObject.quote(err) + ")";
                    runOnUiThread(new Runnable() {
                        public void run() { if (web != null) web.evaluateJavascript(js, null); }
                    });
                }
            }).start();
        }
    }

    static String readStream(InputStream in) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        return new String(out.toByteArray(), "UTF-8");
    }

    static String readFile(File f) {
        if (!f.exists()) return "";
        try {
            FileInputStream in = new FileInputStream(f);
            try { return readStream(in); } finally { in.close(); }
        } catch (Exception e) { return ""; }
    }

    static void writeFile(File f, String text) {
        try {
            File tmp = new File(f.getPath() + ".tmp");
            FileOutputStream out = new FileOutputStream(tmp);
            try { out.write(text.getBytes("UTF-8")); } finally { out.close(); }
            if (!tmp.renameTo(f)) {            // 이름 바꾸기가 안 되면 직접 덮어쓰기
                FileOutputStream o2 = new FileOutputStream(f);
                try { o2.write(text.getBytes("UTF-8")); } finally { o2.close(); }
                tmp.delete();
            }
        } catch (Exception e) { }
    }
}
