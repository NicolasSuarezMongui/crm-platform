import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError } from 'rxjs';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  is_superuser: boolean;
  roles: { id: string; name: string; permissions: Record<string, Record<string, boolean>> }[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly API = '/api/v1/auth';

  // Signals - fuente de verdad del estado de auth
  readonly currentUser = signal<CurrentUser | null>(null);
  readonly isAuthenticated = signal<boolean>(false);
  readonly isLoading = signal<boolean>(false);

  constructor() {
    // Restaurar sesión si hay token guardado
    if (this.getAccessToken()) {
      this.loadCurrentUser().subscribe({
        error: () => this.clearSession(),
      });
    }
  }

  login(email: string, password: string): Observable<TokenResponse> {
    const body = new FormData();
    body.append('username', email);
    body.append('password', password);

    return this.http.post<TokenResponse>(`${this.API}/login`, body).pipe(
      tap((tokens) => {
        this.storeTokens(tokens);
        this.isLoading.set(false);
      }),
      catchError((err) => {
        this.isLoading.set(false);
        return throwError(() => err);
      }),
    );
  }

  refreshToken(): Observable<TokenResponse> {
    const refresh_token = localStorage.getItem('refresh_token') ?? '';
    return this.http
      .post<TokenResponse>(`${this.API}/refresh`, { refresh_token })
      .pipe(tap((tokens) => this.storeTokens(tokens)));
  }

  loadCurrentUser(): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(`${this.API}/me`).pipe(
      tap((user) => {
        this.currentUser.set(user);
        this.isAuthenticated.set(true);
      }),
    );
  }

  logout(): void {
    this.clearSession();
    this.router.navigate(['/auth/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  hasPermission(resource: string, action: string): boolean {
    const user = this.currentUser();
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.roles.some((role) => role.permissions[resource]?.[action] === true);
  }

  private storeTokens(tokens: TokenResponse): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    this.isAuthenticated.set(true);
    this.loadCurrentUser().subscribe();
  }

  private clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
  }
}
