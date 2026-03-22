import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  User,
  UserSummary,
  UserCreate,
  UserUpdate,
  AssignRolesRequest,
  PaginatedResponse,
} from '../models/iam.models';

export interface UserListParams {
  skip?: number;
  limit?: number;
  search?: string;
  is_active?: boolean;
}

@Injectable({ providedIn: 'root' })
export class UsersService {
  private readonly http = inject(HttpClient);
  private readonly BASE = '/api/v1/users';

  list(params: UserListParams = {}): Observable<PaginatedResponse<UserSummary>> {
    let httpParams = new HttpParams();
    if (params.skip != null) httpParams = httpParams.set('skip', params.skip);
    if (params.limit != null) httpParams = httpParams.set('limit', params.limit);
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.is_active != null) httpParams = httpParams.set('is_active', params.is_active);
    return this.http.get<PaginatedResponse<UserSummary>>(this.BASE, { params: httpParams });
  }

  getById(id: string): Observable<User> {
    return this.http.get<User>(`${this.BASE}/${id}`);
  }

  create(data: UserCreate): Observable<User> {
    return this.http.post<User>(this.BASE, data);
  }

  update(id: string, data: UserUpdate): Observable<User> {
    return this.http.patch<User>(`${this.BASE}/${id}`, data);
  }

  deactivate(id: string): Observable<User> {
    return this.http.patch<User>(`${this.BASE}/${id}/deactivate`, {});
  }

  reactivate(id: string): Observable<User> {
    return this.http.patch<User>(`${this.BASE}/${id}/reactivate`, {});
  }

  assignRoles(id: string, data: AssignRolesRequest): Observable<User> {
    return this.http.put<User>(`${this.BASE}/${id}/roles`, data);
  }
}
