import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../../core/services/users.service';
import { UserSummary } from '../../../core/models/iam.models';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-users-list',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './users-list.component.html',
})
export class UsersListComponent implements OnInit {
  private readonly usersService = inject(UsersService);
  protected readonly auth = inject(AuthService);

  protected readonly Math = Math;

  readonly users = signal<UserSummary[]>([]);
  readonly total = signal(0);
  readonly loading = signal(false);
  readonly skip = signal(0);
  readonly pageSize = 20;

  readonly showCreateModal = signal(false);
  readonly creating = signal(false);
  readonly createError = signal<string | null>(null);

  search = '';
  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  readonly activeStatusFilter = signal<boolean | null>(null);

  createForm: Record<string, string> = {
    full_name: '',
    email: '',
    password: '',
  };

  readonly createFields = [
    { key: 'full_name', label: 'Nombre completo', type: 'text', placeholder: 'Jane Doe' },
    { key: 'email', label: 'Email', type: 'email', placeholder: 'jane@empresa.com' },
    { key: 'password', label: 'Contraseña', type: 'password', placeholder: 'Mínimo 8 caracteres' },
  ];

  readonly statusOptions = [
    { label: 'Todos', value: null },
    { label: 'Activos', value: true },
    { label: 'Inactivos', value: false },
  ];

  readonly activeClass = `
    inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
    bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400
  `;
  readonly inactiveClass = `
    inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
    bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400
  `;

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading.set(true);
    this.usersService
      .list({
        skip: this.skip(),
        limit: this.pageSize,
        search: this.search || undefined,
        is_active: this.activeStatusFilter() ?? undefined,
      })
      .subscribe({
        next: (res) => {
          this.users.set(res.items);
          this.total.set(res.total);
          this.loading.set(false);
        },
        error: () => this.loading.set(false),
      });
  }

  onSearchChange(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => {
      this.skip.set(0);
      this.loadUsers();
    }, 350);
  }

  setStatusFilter(value: boolean | null): void {
    this.activeStatusFilter.set(value);
    this.skip.set(0);
    this.loadUsers();
  }

  prevPage(): void {
    this.skip.update((s) => Math.max(0, s - this.pageSize));
    this.loadUsers();
  }

  nextPage(): void {
    this.skip.update((s) => s + this.pageSize);
    this.loadUsers();
  }

  openCreate(): void {
    this.createForm = { full_name: '', email: '', password: '' };
    this.createError.set(null);
    this.showCreateModal.set(true);
  }

  submitCreate(): void {
    if (
      !this.createForm['full_name'] ||
      !this.createForm['email'] ||
      !this.createForm['password']
    ) {
      this.createError.set('Todos los campos son obligatorios');
      return;
    }
    this.creating.set(true);
    this.usersService
      .create({
        full_name: this.createForm['full_name'],
        email: this.createForm['email'],
        password: this.createForm['password'],
      })
      .subscribe({
        next: () => {
          this.creating.set(false);
          this.showCreateModal.set(false);
          this.loadUsers();
        },
        error: (err) => {
          this.creating.set(false);
          this.createError.set(err?.error?.detail ?? 'Error al crear usuario');
        },
      });
  }

  initials(name: string): string {
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }
}
