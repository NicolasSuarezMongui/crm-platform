import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';

export const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell/shell.component').then((m) => m.ShellComponent),
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      // --- IAM -----------------------------------------------------------
      {
        path: 'users',
        canActivate: [permissionGuard('users', 'read')],
        loadComponent: () =>
          import('./features/users/users-list/users-list.component').then(
            (m) => m.UsersListComponent,
          ),
      },
      {
        path: 'users/:id',
        canActivate: [permissionGuard('users', 'read')],
        loadComponent: () =>
          import('./features/users/user-detail/user-detail.component').then(
            (m) => m.UserDetailComponent,
          ),
      },
      {
        path: 'roles',
        canActivate: [permissionGuard('users', 'read')],
        loadComponent: () =>
          import('./features/roles/roles-list/roles-list.component').then(
            (m) => m.RolesListComponent,
          ),
      },
      {
        path: 'roles/new',
        canActivate: [permissionGuard('settings', 'write')],
        loadComponent: () =>
          import('./features/roles/role-form/role-form.component').then((m) => m.RoleFormComponent),
      },
      {
        path: 'roles/:id/edit',
        canActivate: [permissionGuard('settings', 'write')],
        loadComponent: () =>
          import('./features/roles/role-form/role-form.component').then((m) => m.RoleFormComponent),
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },
  { path: '**', redirectTo: '' },
];
