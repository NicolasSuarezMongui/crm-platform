import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { filter, take, map } from 'rxjs';
import { toObservable } from '@angular/core/rxjs-interop';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  // Si no hay token en absoluto, redirect inmediato
  if (!auth.getAccessToken()) {
    return router.createUrlTree(['/auth/login']);
  }

  // Si ya está autenticado, pasar
  if (auth.isAuthenticated()) {
    return true;
  }

  // Hay token pero el usuario aún no cargó - esperar
  return toObservable(auth.isAuthenticated).pipe(
    filter(v => v === true),
    take(1),
    map(() => true)
  );
};
