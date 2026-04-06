import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  ObjectType,
  ObjectTypeSummary,
  ObjectTypeCreate,
  ObjectTypeUpdate,
  FieldDefinition,
  FieldDefinitionCreate,
} from '../models/objects.models';

@Injectable({ providedIn: 'root' })
export class ObjectTypesService {
  private readonly http = inject(HttpClient);
  private readonly BASE = '/api/v1/object-types';

  list(): Observable<ObjectTypeSummary[]> {
    return this.http.get<ObjectTypeSummary[]>(this.BASE);
  }

  getById(id: string): Observable<ObjectType> {
    return this.http.get<ObjectType>(`${this.BASE}/${id}`);
  }

  create(data: ObjectTypeCreate): Observable<ObjectType> {
    return this.http.post<ObjectType>(this.BASE, data);
  }

  update(id: string, data: ObjectTypeUpdate): Observable<ObjectType> {
    return this.http.patch<ObjectType>(`${this.BASE}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.BASE}/${id}`);
  }

  addField(objectTypeId: string, data: FieldDefinitionCreate): Observable<FieldDefinition> {
    return this.http.post<FieldDefinition>(`${this.BASE}/${objectTypeId}/fields`, data);
  }

  deleteField(objectTypeId: string, fieldId: string): Observable<void> {
    return this.http.delete<void>(`${this.BASE}/${objectTypeId}/fields/${fieldId}`);
  }
}
