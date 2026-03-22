import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../../core/services/users.service';
import { RolesService } from '../../../core/services/roles.service';
import { AuthService } from '../../../core/services/auth.service';
import { User, Role } from '../../../core/models/iam.models';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './user-detail.component.html',
})
export class UserDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly usersService = inject(UsersService);
  private readonly rolesService = inject(RolesService);
  protected readonly auth = inject(AuthService);

  readonly user = signal<User | null>(null);
  readonly allRoles = signal<Role[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly savingRoles = signal(false);
  readonly toggling = signal(false);
  readonly editSuccess = signal(false);

  editName = '';
  selectedRoleIds = signal<Set<string>>(new Set());

  readonly canEdit = computed(
    () => this.auth.hasPermission('users', 'write') || this.isOwnProfile(),
  );

  readonly activeClass = `
    inline-flex px-2 py-0.5 rounded-full text-xs font-medium
    bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400
  `;
  readonly inactiveClass = `
    inline-flex px-2 py-0.5 rounded-full text-xs font-medium
    bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400
  `;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.usersService.getById(id).subscribe({
      next: (u) => {
        this.user.set(u);
        this.editName = u.full_name;
        this.selectedRoleIds.set(new Set(u.roles.map((r) => r.id)));
        this.loading.set(false);
      },
      error: () => this.router.navigate(['/users']),
    });
    this.rolesService.list().subscribe((roles) => this.allRoles.set(roles));
  }

  isOwnProfile(): boolean {
    return this.auth.currentUser()?.id === this.user()?.id;
  }

  toggleRole(roleId: string): void {
    this.selectedRoleIds.update((set) => {
      const next = new Set(set);
      next.has(roleId) ? next.delete(roleId) : next.add(roleId);
      return next;
    });
  }

  isRoleSelected(roleId: string): boolean {
    return this.selectedRoleIds().has(roleId);
  }

  saveEdit(): void {
    if (!this.editName.trim() || !this.user()) return;
    this.saving.set(true);
    this.usersService.update(this.user()!.id, { full_name: this.editName }).subscribe({
      next: (u) => {
        this.user.set(u);
        this.saving.set(false);
        this.editSuccess.set(true);
        setTimeout(() => this.editSuccess.set(false), 3000);
      },
      error: () => this.saving.set(false),
    });
  }

  saveRoles(): void {
    if (!this.user()) return;
    this.savingRoles.set(true);
    this.usersService
      .assignRoles(this.user()!.id, {
        role_ids: Array.from(this.selectedRoleIds()),
      })
      .subscribe({
        next: (u) => {
          this.user.set(u);
          this.savingRoles.set(false);
        },
        error: () => this.savingRoles.set(false),
      });
  }

  toggleActive(activate: boolean): void {
    if (!this.user()) return;
    this.toggling.set(true);
    const call = activate
      ? this.usersService.reactivate(this.user()!.id)
      : this.usersService.deactivate(this.user()!.id);

    call.subscribe({
      next: (u) => {
        this.user.set(u);
        this.toggling.set(false);
      },
      error: () => this.toggling.set(false),
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
      month: 'long',
      year: 'numeric',
    });
  }
}
