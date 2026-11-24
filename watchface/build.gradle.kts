plugins {
    id("com.android.application")
}

android {
    // Nazwa pakietu jest stała po pierwszej publikacji w Google Play.
    namespace = "com.glucosechrono.watchface"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.glucosechrono.watchface"
        // Watch Face Format v2 wymaga Wear OS 5 (API 34)
        minSdk = 34
        targetSdk = 35
        // Workflow „Release” podaje kolejny numer (-PversionCode), jak wymaga Google Play.
        versionCode = (project.findProperty("versionCode") as String?)?.toInt() ?: 1
        versionName = (project.findProperty("versionName") as String?) ?: "1.0"
    }

    signingConfigs {
        // Klucz przesyłania do Google Play, z sekretów GitHub (patrz docs/PLAY.md).
        val keystore = System.getenv("UPLOAD_KEYSTORE_FILE")
        if (keystore != null) {
            create("upload") {
                storeFile = file(keystore)
                storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
                keyAlias = "upload"
                keyPassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Z kluczem przesyłania, gdy jest dostępny; inaczej klucz debug (APK do wgrania ręcznie).
            signingConfig = signingConfigs.findByName("upload") ?: signingConfigs.getByName("debug")
        }
    }
}
