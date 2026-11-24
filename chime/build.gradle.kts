plugins {
    id("com.android.application")
}

android {
    // Osobna aplikacja: tarcza WFF nie może zawierać kodu, a dźwięk wymaga kodu.
    namespace = "com.glucosechrono.chime"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.glucosechrono.chime"
        minSdk = 30
        targetSdk = 35
        versionCode = (project.findProperty("versionCode") as String?)?.toInt() ?: 1
        versionName = (project.findProperty("versionName") as String?) ?: "1.0"
    }

    signingConfigs {
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
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
            signingConfig = signingConfigs.findByName("upload") ?: signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
