import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CrmRecord, RecordCreate, RecordUpdate } from '../models/objects.models';
import { PaginatedResponse } from '../models/iam.models';

export interface RecordListParams {
  object_type: string;
  skip?: number;
  limit?: number;
  search?: string;
  stage?: string;
  owner_id?: string;
}

@Injectable({ providedIn: 'root' })
export class RecordsService {
  private readonly http = inject(HttpClient);
  private readonly BASE = '/api/v1/records';

  list(params: RecordListParams): Observable<PaginatedResponse<CrmRecord>> {
    let p = new HttpParams().set('object_type', params.object_type);
    if (params.skip != null) p = p.set('skip', params.skip);
    if (params.limit != null) p = p.set('limit', params.limit);
    if (params.search) p = p.set('search', params.search);
    if (params.stage) p = p.set('stage', params.stage);
    if (params.owner_id) p = p.set('owner_id', params.owner_id);
    return this.http.get<PaginatedResponse<CrmRecord>>(this.BASE, { params: p });
  }

  getById(id: string): Observable<CrmRecord> {
    return this.http.get<CrmRecord>(`${this.BASE}/${id}`);
  }

  create(objectType: string, data: RecordCreate): Observable<CrmRecord> {
    return this.http.post<CrmRecord>(`${this.BASE}?object_type=${objectType}`, data);
  }

  update(id: string, data: RecordUpdate): Observable<CrmRecord> {
    return this.http.patch<CrmRecord>(`${this.BASE}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.BASE}/${id}`);
  }
}
