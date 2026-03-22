// core/guards/permission.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { filter, map, take } from 'rxjs';
import { toObservable } from '@angular/core/rxjs-interop';

export function permissionGuard(resource: string, action: string): CanActivateFn {
  return (_route: ActivatedRouteSnapshot) => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.getAccessToken()) {
      return router.createUrlTree(['/auth/login']);
    }

    // Si ya tenemos usuario cargado, evaluar permiso directamente
    if (auth.isAuthenticated()) {
      return auth.hasPermission(resource, action)
        ? true
        : router.createUrlTree(['/dashboard']);
    }

    // Esperar a que el usuario cargue y luego evaluar
    return toObservable(auth.isAuthenticated).pipe(
      filter(v => v === true),
      take(1),
      map(() => {
        return auth.hasPermission(resource, action)
          ? true
          : router.createUrlTree(['/dashboard']);
      })
    );
  };
}