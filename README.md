# Resonance / Book Match — Android

Готовий Android-проєкт Resonance Book Match, підготовлений під ланцюжок:
**Termux → GitHub → GitHub Actions → APK → телефон**.

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
- `termux-build.sh` сам створює локальний git, GitHub repository, push, запускає Actions і завантажує APK artifact.

## Termux

У цьому проєкті не використовується MOR-mesh. Це окремий repository `resonance-book-match`.

### 1. Встановити інструменти

```bash
pkg update
pkg install git gh unzip -y
```

### 2. Авторизувати GitHub

```bash
gh auth login
```

Вибрати:

- GitHub.com
- HTTPS
- Login with a web browser

### 3. Розпакувати цей ZIP і зайти в каталог

```bash
cd ~/storage/downloads
unzip -o resonance-book-match-repo.zip
cd resonance-book-match-repo
chmod +x termux-build.sh
```

### 4. Один запуск

```bash
./termux-build.sh
```

Скрипт:

1. перевіряє GitHub login;
2. створює локальний git repository, якщо його ще немає;
3. створює `allojack69-ops/resonance-book-match`, якщо remote ще не існує;
4. робить push у `main`;
5. запускає GitHub Actions;
6. чекає завершення build;
7. завантажує APK;
8. копіює його як `resonance-book-match.apk`.

### 5. Встановити APK

```bash
cp resonance-book-match.apk /sdcard/Download/
```

Потім у файловому менеджері Android відкрий:

`Download/resonance-book-match.apk`

і встанови застосунок.

## Якщо repository вже існує

Можна залишити назву за замовчуванням або вказати іншу:

```bash
RESONANCE_REPO="allojack69-ops/назва" ./termux-build.sh
```
