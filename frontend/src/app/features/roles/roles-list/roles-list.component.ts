import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RolesService } from '../../../core/services/roles.service';
import { AuthService } from '../../../core/services/auth.service';
import { Role } from '../../../core/models/iam.models';

const RESOURCES = [
  'users',
  'contacts',
  'accounts',
  'deals',
  'reports',
  'settings',
  'bulk_import',
  'object_types',
];

@Component({
  selector: 'app-roles-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './roles-list.component.html',
})
export class RolesListComponent implements OnInit {
  private readonly rolesService = inject(RolesService);
  protected readonly auth = inject(AuthService);

  readonly roles = signal<Role[]>([]);
  readonly loading = signal(true);
  readonly deleteTarget = signal<Role | null>(null);
  readonly deleting = signal(false);
  readonly deleteError = signal<string | null>(null);

  readonly resources = RESOURCES;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.rolesService.list().subscribe({
      next: (roles) => {
        this.roles.set(roles);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  deleteRole(role: Role): void {
    this.deleteError.set(null);
    this.deleteTarget.set(role);
  }

  confirmDelete(): void {
    const role = this.deleteTarget();
    if (!role) return;
    this.deleting.set(true);
    this.rolesService.delete(role.id).subscribe({
      next: () => {
        this.deleting.set(false);
        this.deleteTarget.set(null);
        this.load();
      },
      error: (err) => {
        this.deleting.set(false);
        this.deleteError.set(err?.error?.detail ?? 'No se pudo eliminar el rol');
      },
    });
  }
}
