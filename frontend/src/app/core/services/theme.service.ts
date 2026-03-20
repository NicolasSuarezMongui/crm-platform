import { Injectable, signal, effect, inject } from '@angular/core';
import { DOCUMENT } from '@angular/core';

export type Theme = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly document = inject(DOCUMENT);
  private readonly STORAGE_KEY = 'crm-theme';

  readonly theme = signal<Theme>(this.getInitialTheme());

  constructor() {
    // Aplica la clase al <html> cada vez que cambia el signal
    effect(() => {
      const t = this.theme();
      const html = this.document.documentElement;
      html.classList.toggle('dark', t === 'dark');
      localStorage.setItem(this.STORAGE_KEY, t);
    });
  }

  toggle(): void {
    this.theme.update((t) => (t === 'light' ? 'dark' : 'light'));
  }

  private getInitialTheme(): Theme {
    const stored = localStorage.getItem(this.STORAGE_KEY) as Theme | null;
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
}
