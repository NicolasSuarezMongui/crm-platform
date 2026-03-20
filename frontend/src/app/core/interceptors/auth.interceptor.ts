import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpErrorResponse,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

// Rutas que nunca deben llevar el header de auth
const PUBLIC_ROUTES = ['/auth/login', '/auth/register', '/auth/refresh'];

const isPublicRoute = (url: string): boolean => PUBLIC_ROUTES.some((route) => url.includes(route));

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) => {
  const authService = inject(AuthService);
  const token = authService.getAccessToken();

  const authReq =
    token && !isPublicRoute(req.url)
      ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
      : req;

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      // Solo intentar refresh en 401 y si no es ya una ruta de auth
      if (err.status === 401 && !isPublicRoute(req.url)) {
        return authService.refreshToken().pipe(
          switchMap(() => {
            const newToken = authService.getAccessToken();
            const retryReq = req.clone({ setHeaders: { Authorization: `Bearer ${newToken}` } });
            return next(retryReq);
          }),
          catchError((refreshErr) => {
            // Refresh falló - sesión expirada, logout
            authService.logout();
            return throwError(() => refreshErr);
          }),
        );
      }
      return throwError(() => err);
    }),
  );
};
