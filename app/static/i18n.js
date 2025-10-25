// Simple i18n system
class I18n {
    constructor() {
        this.translations = {};
        this.currentLanguage = 'en';
        this.fallbackLanguage = 'en';
    }

    async loadLanguage(lang) {
        try {
            const response = await fetch(`/static/translations/${lang}.json`);
            if (response.ok) {
                this.translations[lang] = await response.json();
                this.currentLanguage = lang;
                return true;
            }
        } catch (error) {
            console.error(`Failed to load language ${lang}:`, error);
        }
        return false;
    }

    async init(preferredLanguage = null) {
        // Detect browser language if not specified
        const browserLang = preferredLanguage || navigator.language.split('-')[0];
        
        // Always load English as fallback
        await this.loadLanguage(this.fallbackLanguage);
        
        // Try to load preferred language
        if (browserLang !== this.fallbackLanguage) {
            const loaded = await this.loadLanguage(browserLang);
            if (!loaded) {
                this.currentLanguage = this.fallbackLanguage;
            }
        }
    }

    t(key, replacements = {}) {
        let text = this.translations[this.currentLanguage]?.[key] 
                   || this.translations[this.fallbackLanguage]?.[key] 
                   || key;
        
        // Replace placeholders like {count}, {error}, etc.
        Object.keys(replacements).forEach(placeholder => {
            text = text.replace(`{${placeholder}}`, replacements[placeholder]);
        });
        
        return text;
    }

    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLanguage = lang;
            return true;
        }
        return false;
    }

    getAvailableLanguages() {
        return Object.keys(this.translations);
    }
}

// Global instance
const i18n = new I18n();
