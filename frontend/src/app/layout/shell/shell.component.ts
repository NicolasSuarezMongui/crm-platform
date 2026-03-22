import { Component, inject, signal, computed } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ThemeToggleComponent } from '../../shared/components/theme-toggle/theme-toggle.component';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  permission?: { resource: string; action: string };
  section?: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ThemeToggleComponent],
  templateUrl: './shell.component.html',
})
export class ShellComponent {
  protected readonly auth = inject(AuthService);

  readonly collapsed = signal(false);
  readonly mobileOpen = signal(false);

  readonly sidebarClass = computed(() => (this.collapsed() ? 'w-14' : 'w-56'));

  readonly userInitials = computed(() => {
    const name = this.auth.currentUser()?.full_name ?? '';
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  });

  readonly navSections = computed(() => [
    {
      title: 'General',
      items: [
        {
          label: 'Dashboard',
          route: '/dashboard',
          icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>`,
        },
      ],
    },
    {
      title: 'Administración',
      items: [
        {
          label: 'Usuarios',
          route: '/users',
          icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
          permission: { resource: 'users', action: 'read' },
        },
        {
          label: 'Roles',
          route: '/roles',
          icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>`,
          permission: { resource: 'users', action: 'read' },
        },
      ],
    },
  ]);

  canSee(item: NavItem): boolean {
    if (!item.permission) return true;
    return this.auth.hasPermission(item.permission.resource, item.permission.action);
  }
}
