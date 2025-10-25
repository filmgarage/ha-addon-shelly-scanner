# Translations

This directory contains translation files for the Shelly Device Scanner interface.

## Available Languages

- `en.json` - English (default/fallback)
- `nl.json` - Nederlands (Dutch)

## Adding a New Language

1. Copy `en.json` to a new file with your language code (e.g., `de.json` for German, `fr.json` for French)
2. Translate all values (keep the keys in English!)
3. Test by changing your browser language or adding `?lang=de` to the URL

## Translation File Format

```json
{
  "key_name": "Translated text",
  "with_placeholder": "Text with {variable} placeholder"
}
```

### Important Rules

- **Keys** must remain in English (e.g., `"app_title"`)
- **Values** contain the translated text
- **Placeholders** like `{count}`, `{error}` must remain unchanged
- Use UTF-8 encoding for special characters

## Supported Placeholders

- `{count}` - Number of devices found
- `{error}` - Error message text

## Language Detection

The app automatically detects the browser language and loads the appropriate translation file. If a translation doesn't exist, it falls back to English.

## Testing

To test a specific language without changing browser settings:

```javascript
// In browser console:
await i18n.loadLanguage('nl');
updateUIText();
```

## Contributing

Want to add a translation? 

1. Fork the repository
2. Add your language file in `app/static/translations/`
3. Test it thoroughly
4. Submit a pull request

Thank you for helping make this tool accessible to more users! 🌍
