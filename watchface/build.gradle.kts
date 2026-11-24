plugins {
    id("com.android.application")
}

android {
    namespace = "com.tarczaglukoza.watchface"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.tarczaglukoza.watchface"
        // Watch Face Format v2 wymaga Wear OS 5 (API 34)
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Na razie podpis debug, żeby dało się wgrać na zegarek. Do Google Play podmienimy na własny klucz.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
