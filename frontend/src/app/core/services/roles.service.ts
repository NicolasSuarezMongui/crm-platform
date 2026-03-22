import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Role, RoleWithUsers, RoleCreate, RoleUpdate } from '../models/iam.models';

@Injectable({ providedIn: 'root' })
export class RolesService {
  private readonly http = inject(HttpClient);
  private readonly BASE = '/api/v1/roles';

  list(): Observable<Role[]> {
    return this.http.get<Role[]>(this.BASE);
  }

  getById(id: string): Observable<RoleWithUsers> {
    return this.http.get<RoleWithUsers>(`${this.BASE}/${id}`);
  }

  create(data: RoleCreate): Observable<Role> {
    return this.http.post<Role>(this.BASE, data);
  }

  update(id: string, data: RoleUpdate): Observable<Role> {
    return this.http.patch<Role>(`${this.BASE}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.BASE}/${id}`);
  }
}
