import { Component, inject, signal, computed } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';
import { ThemeToggleComponent } from '../../../shared/components/theme-toggle/theme-toggle.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink, ThemeToggleComponent],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  // Estado del formulario con signals
  email = '';
  password = '';
  readonly showPassword = signal(false);
  readonly errorMessage = signal<string | null>(null);

  readonly stats = [
    { value: '0', label: 'Contactos' },
    { value: '0', label: 'Deals' },
    { value: '0', label: 'Tareas' },
  ];

  readonly demoAccounts = [
    { label: 'Admin', email: 'admin@crm.local', password: 'admin1234' },
    { label: 'Sales', email: 'sales@crm.local', password: 'sales1234' },
    { label: 'Viewer', email: 'viewer@crm.local', password: 'viewer1234' },
  ];

  // Clase del input como computed para no repetirla 2 veces en el template
  readonly inputClass = computed(
    () => `
    w-full pl-10 pr-4 py-2.5 rounded-lg text-sm
    bg-white dark:bg-slate-800/60 border border-slate-200
    dark:border-slate-700 text-slate-900 dark:text-slate-100
    placeholder:text-slate-400 dark:placeholder:text-slate-500
    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
    dark:focus:ring-indigo-500 transition-colors duration-150
  `,
  );

  fillDemo(demo: { email: string; password: string }): void {
    ((this.email = demo.email), (this.password = demo.password), this.errorMessage.set(null));
  }

  onSubmit(): void {
    if (!this.email || !this.password) return;
    this.errorMessage.set(null);

    this.authService.login(this.email, this.password).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        const status = err?.status;
        if (status === 401) {
          this.errorMessage.set('Correo o contraseña incorrectos.');
        } else if (status === 0) {
          this.errorMessage.set(
            'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.',
          );
        } else {
          this.errorMessage.set('Ocurrió un error inesperado. Intenta de nuevo.');
        }
      },
    });
  }
}
