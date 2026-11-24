# Publikacja w Google Play

Pakiet: `com.glucosechrono.watchface` (stały po pierwszej publikacji).
Podpisywanie: **Play App Signing** — Google trzyma klucz, którym podpisuje instalowane aplikacje, a my podpisujemy
przesyłane pakiety osobnym **kluczem przesyłania** (sekrety GitHub). Zgubiony klucz przesyłania można zresetować przez
pomoc Google Play.

## 1. Sekrety (raz)
GitHub › repozytorium › Settings › Secrets and variables › Actions › **New repository secret**:
- `UPLOAD_KEYSTORE_BASE64` — zawartość pliku `UPLOAD_KEYSTORE_BASE64.txt`,
- `UPLOAD_KEYSTORE_PASSWORD` — zawartość pliku `UPLOAD_KEYSTORE_PASSWORD.txt`.

## 2. Zbuduj pakiet
Actions › **Release (Google Play)** › Run workflow. Gotowy plik:
https://github.com/PrzeBuj/glucose-chrono-watchface/releases/download/play/glucose-chrono-watchface.aab

## 3. Pierwsze wydanie w Play Console (raz, ręcznie — API Google nie pozwala utworzyć nowej aplikacji)
1. **Utwórz aplikację**: nazwa „Glucose Chrono”, aplikacja, bezpłatna.
2. **Test and release › Advanced settings › Form factors** (Ustawienia zaawansowane › Formaty): dodaj **Wear OS**.
   Google Play wymaga osobnej ścieżki Wear OS — pakiet wgrany na zwykłą ścieżkę (telefon) zostanie odrzucony.
3. **Testing › Internal testing**: u góry przełącz ścieżkę na **Wear OS**, dodaj siebie do testerów (lista e-mail),
   **Create new release**, wgraj plik AAB, zapisz i wdroż.
4. Otwórz link dla testerów na telefonie, zaakceptuj, potem zainstaluj tarczę ze Sklepu Play na zegarku
   (albo z telefonu: Sklep Play › wybierz zegarek jako urządzenie).

## 4. (Opcjonalnie) automatyczne wysyłanie, jak w Friend Radar
Workflow może sam wysyłać pakiet do testów wewnętrznych jako konto `github-deploy` z projektu `friend-radar-354a3`.
1. W Cloud Shell (https://shell.cloud.google.com) wklej:
   ```sh
   gcloud iam workload-identity-pools providers create-oidc glucose-chrono \
     --project=friend-radar-354a3 --location=global --workload-identity-pool=github \
     --issuer-uri="https://token.actions.githubusercontent.com" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
     --attribute-condition="assertion.repository == 'PrzeBuj/glucose-chrono-watchface' && assertion.ref == 'refs/heads/main'"
   gcloud iam service-accounts add-iam-policy-binding github-deploy@friend-radar-354a3.iam.gserviceaccount.com \
     --project=friend-radar-354a3 --role=roles/iam.workloadIdentityUser \
     --member="principalSet://iam.googleapis.com/projects/136179368301/locations/global/workloadIdentityPools/github/attribute.repository/PrzeBuj/glucose-chrono-watchface"
   ```
2. Play Console › **Users and permissions** › `github-deploy@friend-radar-354a3.iam.gserviceaccount.com` › dodaj
   aplikację Glucose Chrono z uprawnieniem *Release apps to testing tracks*.
3. GitHub › Settings › Secrets and variables › Actions › **Variables**:
   - `PLAY_UPLOAD` = `true`
   - `WIF_PROVIDER` = `projects/136179368301/locations/global/workloadIdentityPools/github/providers/glucose-chrono`
   - `WIF_SERVICE_ACCOUNT` = `github-deploy@friend-radar-354a3.iam.gserviceaccount.com`

Od tej pory „Run workflow” od razu wysyła nową wersję do testerów.
