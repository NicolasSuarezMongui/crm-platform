import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RolesService } from '../../../core/services/roles.service';
import { ResourcePermissions } from '../../../core/models/iam.models';

interface PermissionDef {
  resource: string;
  label: string;
  actions: { key: string; label: string }[];
}

const PERMISSION_DEFS: PermissionDef[] = [
  {
    resource: 'users',
    label: 'Usuarios',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Crear/Editar' },
      { key: 'delete', label: 'Eliminar' },
    ],
  },
  {
    resource: 'contacts',
    label: 'Contactos',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Crear/Editar' },
      { key: 'delete', label: 'Eliminar' },
    ],
  },
  {
    resource: 'accounts',
    label: 'Cuentas',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Crear/Editar' },
      { key: 'delete', label: 'Eliminar' },
    ],
  },
  {
    resource: 'deals',
    label: 'Oportunidades',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Crear/Editar' },
      { key: 'delete', label: 'Eliminar' },
    ],
  },
  {
    resource: 'reports',
    label: 'Reportes',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Crear' },
    ],
  },
  {
    resource: 'settings',
    label: 'Configuración',
    actions: [
      { key: 'read', label: 'Ver' },
      { key: 'write', label: 'Editar' },
    ],
  },
  {
    resource: 'bulk_import',
    label: 'Importación masiva',
    actions: [{ key: 'execute', label: 'Ejecutar' }],
  },
  {
    resource: 'object_types',
    label: 'Tipos de objeto',
    actions: [{ key: 'manage', label: 'Administrar' }],
  },
];

@Component({
  selector: 'app-role-form',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './role-form.component.html',
})
export class RoleFormComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly rolesService = inject(RolesService);

  readonly isEdit = signal(false);
  readonly loadingRole = signal(false);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);

  private roleId: string | null = null;

  // Form state
  name = '';
  description = '';
  permissions = signal<ResourcePermissions>({});

  readonly permissionDefs = PERMISSION_DEFS;

  ngOnInit(): void {
    this.roleId = this.route.snapshot.paramMap.get('id');
    if (this.roleId) {
      this.isEdit.set(true);
      this.loadingRole.set(true);
      this.rolesService.getById(this.roleId).subscribe({
        next: (role) => {
          this.name = role.name;
          this.description = role.description ?? '';
          this.permissions.set(structuredClone(role.permissions));
          this.loadingRole.set(false);
        },
        error: () => this.router.navigate(['/roles']),
      });
    } else {
      // Initialize all permissions to false
      const initial: ResourcePermissions = {};
      for (const def of PERMISSION_DEFS) {
        initial[def.resource] = {};
        for (const action of def.actions) {
          initial[def.resource][action.key] = false;
        }
      }
      this.permissions.set(initial);
    }
  }

  getPermission(resource: string, action: string): boolean {
    return this.permissions()[resource]?.[action] === true;
  }

  togglePermission(resource: string, action: string): void {
    this.permissions.update((p) => {
      const next = structuredClone(p);
      if (!next[resource]) next[resource] = {};
      next[resource][action] = !next[resource][action];
      return next;
    });
  }

  allSelected(def: PermissionDef): boolean {
    return def.actions.every((a) => this.getPermission(def.resource, a.key));
  }

  toggleResource(def: PermissionDef): void {
    const all = this.allSelected(def);
    this.permissions.update((p) => {
      const next = structuredClone(p);
      if (!next[def.resource]) next[def.resource] = {};
      for (const action of def.actions) {
        next[def.resource][action.key] = !all;
      }
      return next;
    });
  }

  clearAll(): void {
    this.permissions.update((p) => {
      const next = structuredClone(p);
      for (const key of Object.keys(next)) {
        for (const action of Object.keys(next[key])) {
          next[key][action] = false;
        }
      }
      return next;
    });
  }

  submit(): void {
    if (!this.name.trim()) {
      this.error.set('El nombre del rol es obligatorio');
      return;
    }
    this.error.set(null);
    this.saving.set(true);

    const data = {
      name: this.name.trim(),
      description: this.description.trim() || undefined,
      permissions: this.permissions(),
    };

    const call = this.isEdit()
      ? this.rolesService.update(this.roleId!, data)
      : this.rolesService.create(data);

    call.subscribe({
      next: () => this.router.navigate(['/roles']),
      error: (err) => {
        this.saving.set(false);
        this.error.set(err?.error?.detail ?? 'Error al guardar el rol');
      },
    });
  }
}
