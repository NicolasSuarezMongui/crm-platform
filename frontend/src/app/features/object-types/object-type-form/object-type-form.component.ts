import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ObjectTypesService } from '../../../core/services/object-type.service';
import {
  ObjectType,
  FieldDefinition,
  FieldDefinitionCreate,
  FieldType,
  FIELD_TYPE_LABELS,
} from '../../../core/models/objects.models';

const COLORS = [
  '#6366f1',
  '#0ea5e9',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
];

@Component({
  selector: 'app-object-type-form',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './object-type-form.component.html',
})
export class ObjectTypeFormComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly service = inject(ObjectTypesService);

  readonly isEdit = signal(false);
  readonly isSystemType = signal(false);
  readonly loadingType = signal(false);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);

  readonly existingFields = signal<FieldDefinition[]>([]);
  readonly newFields = signal<FieldDefinitionCreate[]>([]);

  private objectTypeId: string | null = null;

  // Form
  label = '';
  labelPlural = '';
  apiName = '';
  description = '';
  color = '#6366f1';

  readonly colors = COLORS;
  readonly inputClass = `
    w-full px-3 py-2 rounded-lg text-sm
    bg-slate-50 dark:bg-slate-900
    border border-slate-200 dark:border-slate-700
    text-slate-900 dark:text-slate-100
    placeholder:text-slate-400
    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  readonly fieldTypes = Object.entries(FIELD_TYPE_LABELS).map(([value, label]) => ({
    value,
    label,
  }));

  ngOnInit(): void {
    this.objectTypeId = this.route.snapshot.paramMap.get('id');
    if (this.objectTypeId) {
      this.isEdit.set(true);
      this.loadingType.set(true);
      this.service.getById(this.objectTypeId).subscribe({
        next: (ot) => {
          this.label = ot.label;
          this.labelPlural = ot.label_plural;
          this.description = ot.description ?? '';
          this.color = ot.color ?? '#6366f1';
          this.isSystemType.set(ot.is_system);
          this.existingFields.set(
            [...ot.field_definitions].sort((a, b) => a.sort_order - b.sort_order),
          );
          this.loadingType.set(false);
        },
        error: () => this.router.navigate(['/object-types']),
      });
    }
  }

  addFieldRow(): void {
    this.newFields.update((f) => [
      ...f,
      {
        api_name: '',
        label: '',
        field_type: 'text' as FieldType,
        is_required: false,
        is_searchable: true,
        sort_order: 0,
        options: {},
      },
    ]);
  }

  removeFieldRow(index: number): void {
    this.newFields.update((f) => f.filter((_, i) => i !== index));
  }

  deleteExistingField(field: FieldDefinition): void {
    if (!this.objectTypeId) return;
    this.service.deleteField(this.objectTypeId, field.id).subscribe({
      next: () => this.existingFields.update((f) => f.filter((x) => x.id !== field.id)),
      error: (err) => this.error.set(err?.error?.detail ?? 'Error al eliminar campo'),
    });
  }

  fieldTypeLabel(ft: string): string {
    return FIELD_TYPE_LABELS[ft as FieldType] ?? ft;
  }

  async submit(): Promise<void> {
    if (!this.label.trim() || !this.labelPlural.trim()) {
      this.error.set('Nombre y plural son obligatorios');
      return;
    }
    this.error.set(null);
    this.saving.set(true);

    if (this.isEdit()) {
      // Update basic info first
      this.service
        .update(this.objectTypeId!, {
          label: this.label,
          label_plural: this.labelPlural,
          description: this.description || undefined,
          color: this.color,
        })
        .subscribe({
          next: async () => {
            // Then add new fields sequentially
            for (const field of this.newFields()) {
              if (!field.api_name || !field.label) continue;
              await this.service.addField(this.objectTypeId!, field).toPromise();
            }
            this.saving.set(false);
            this.router.navigate(['/object-types']);
          },
          error: (err) => {
            this.saving.set(false);
            this.error.set(err?.error?.detail ?? 'Error al guardar');
          },
        });
    } else {
      if (!this.apiName.trim()) {
        this.error.set('El API name es obligatorio');
        this.saving.set(false);
        return;
      }
      this.service
        .create({
          api_name: this.apiName,
          label: this.label,
          label_plural: this.labelPlural,
          description: this.description || undefined,
          color: this.color,
          fields: this.newFields().filter((f) => f.api_name && f.label),
        })
        .subscribe({
          next: () => {
            this.saving.set(false);
            this.router.navigate(['/object-types']);
          },
          error: (err) => {
            this.saving.set(false);
            this.error.set(err?.error?.detail ?? 'Error al crear tipo');
          },
        });
    }
  }
}
