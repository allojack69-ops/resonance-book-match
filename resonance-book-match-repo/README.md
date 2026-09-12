# Resonance / Book Match — Android

Готовий Android-проєкт Resonance Book Match, підготовлений під схему: **Termux → GitHub → GitHub Actions → APK → Termux**.

## Що всередині

- Android WebView application.
- Поточний Resonance Book Match продукт у `app/src/main/assets/index.html`.
- 12 behavioral stimuli.
- Preference Graph із позитивними сигналами.
- Direct Match / Bridge / Discovery.
- Для непрочитаної книги: **Не цікаво / Трохи цікаво / Цікаво / Дуже цікаво**.
- Для прочитаної книги — окреме реальне враження.
- Feedback зберігається локально та експортується в JSON.
- GitHub Actions автоматично збирає `app-debug.apk`.
- `termux-build.sh` автоматизує створення GitHub repo, push, запуск Actions і завантаження APK artifact.

## 1. Підготувати Termux

```bash
pkg update
pkg install git gh
```

Авторизувати GitHub один раз:

```bash
gh auth login
```

## 2. Запустити збірку

Розпакуй цей проєкт у Termux, перейди в його каталог і виконай:

```bash
./termux-build.sh
```

За замовчуванням скрипт використовує:

```text
allojack69-ops/resonance-book-match
```

Якщо repository має іншу назву:

```bash
RESONANCE_REPO="allojack69-ops/назва-репозиторію" ./termux-build.sh
```

Скрипт:

1. перевірить `gh auth`;
2. якщо git remote ще немає — створить GitHub repository через `gh repo create`;
3. завантажить код у `main`;
4. запустить `.github/workflows/build-apk.yml`;
5. дочекається завершення Actions;
6. завантажить artifact `resonance-book-match-apk` у `dist/resonance-book-match-apk/`.

## 3. Якщо треба лише push

```bash
git add .
git commit -m "Update Resonance Book Match"
git push
```

Push у `main` також автоматично запускає GitHub Actions.

## 4. APK

Після успішного workflow APK буде тут:

```text
app/build/outputs/apk/debug/app-debug.apk
```

А через `termux-build.sh` — локально в:

```text
dist/resonance-book-match-apk/app-debug.apk
```

## Важливо

Сам GitHub repository не створюється з цього середовища безпосередньо, тому створення зроблене через `gh repo create` у Termux. Це той самий практичний ланцюжок: **код → GitHub → Actions → APK**.
