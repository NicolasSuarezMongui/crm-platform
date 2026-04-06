import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RecordsService } from '../../../core/services/records.service';
import { ObjectTypesService } from '../../../core/services/object-type.service';
import { AuthService } from '../../../core/services/auth.service';
import { CrmRecord, ObjectType, FieldDefinition } from '../../../core/models/objects.models';
import { FieldInputComponent } from '../../../shared/components/field-input/field-input.component';

@Component({
  selector: 'app-records-list',
  standalone: true,
  imports: [RouterLink, FormsModule, FieldInputComponent],
  templateUrl: './records-list.component.html',
})
export class RecordsListComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly recordsService = inject(RecordsService);
  private readonly objectTypesService = inject(ObjectTypesService);
  protected readonly auth = inject(AuthService);
  protected readonly Math = Math;

  readonly apiName = signal('');
  readonly objectType = signal<ObjectType | null>(null);
  readonly records = signal<CrmRecord[]>([]);
  readonly total = signal(0);
  readonly loading = signal(true);
  readonly skip = signal(0);
  readonly pageSize = 20;

  readonly showCreateModal = signal(false);
  readonly creating = signal(false);
  readonly createError = signal<string | null>(null);

  createForm: Record<string, string> = { name: '' };
  createFormData: Record<string, unknown> = {};
  createErrors: Record<string, string> = {};

  search = '';
  stageFilter = '';
  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  // Columns to show in the table (first 3 non-required non-long fields)
  readonly visibleColumns = computed(() => {
    const fields = this.objectType()?.field_definitions ?? [];
    return fields
      .filter((f) => !['long_text', 'relation', 'boolean'].includes(f.field_type))
      .sort((a, b) => a.sort_order - b.sort_order)
      .slice(0, 3);
  });

  readonly stageOptions = computed(() => {
    const fields = this.objectType()?.field_definitions ?? [];
    const stageField = fields.find((f) => f.api_name === 'stage' && f.field_type === 'select');
    return (stageField?.options['options'] as { value: string; label: string }[]) ?? [];
  });

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.apiName.set(params['objectType']);
      this.loadObjectType();
    });
  }

  loadObjectType(): void {
    // Find by api_name from the summary list
    this.objectTypesService.list().subscribe((types) => {
      const summary = types.find((t) => t.api_name === this.apiName());
      if (summary) {
        this.objectTypesService.getById(summary.id).subscribe((full) => {
          this.objectType.set(full);
          this.loadRecords();
        });
      }
    });
  }

  loadRecords(): void {
    this.loading.set(true);
    this.recordsService
      .list({
        object_type: this.apiName(),
        skip: this.skip(),
        limit: this.pageSize,
        search: this.search || undefined,
        stage: this.stageFilter || undefined,
      })
      .subscribe({
        next: (res) => {
          this.records.set(res.items);
          this.total.set(res.total);
          this.loading.set(false);
        },
        error: () => this.loading.set(false),
      });
  }

  reload(): void {
    this.skip.set(0);
    this.loadRecords();
  }

  onSearch(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => this.reload(), 350);
  }

  prevPage(): void {
    this.skip.update((s) => Math.max(0, s - this.pageSize));
    this.loadRecords();
  }
  nextPage(): void {
    this.skip.update((s) => s + this.pageSize);
    this.loadRecords();
  }

  openCreate(): void {
    this.createForm = { name: '' };
    this.createFormData = {};
    this.createErrors = {};
    this.createError.set(null);
    this.showCreateModal.set(true);
  }

  submitCreate(): void {
    if (!this.createForm['name']?.trim()) {
      this.createError.set('El nombre es obligatorio');
      return;
    }
    this.creating.set(true);
    this.createErrors = {};
    this.createError.set(null);

    this.recordsService
      .create(this.apiName(), {
        name: this.createForm['name'],
        data: this.createFormData,
      })
      .subscribe({
        next: () => {
          this.creating.set(false);
          this.showCreateModal.set(false);
          this.loadRecords();
        },
        error: (err) => {
          this.creating.set(false);
          const detail = err?.error?.detail;
          if (detail?.errors) {
            this.createErrors = detail.errors;
          } else {
            this.createError.set(detail?.message ?? detail ?? 'Error al crear');
          }
        },
      });
  }

  formatFieldValue(value: unknown, field: FieldDefinition): string {
    if (value == null) return '—';
    if (field.field_type === 'select') {
      const opts = (field.options['options'] as { value: string; label: string }[]) ?? [];
      return opts.find((o) => o.value === value)?.label ?? String(value);
    }
    if (field.field_type === 'boolean') return value ? 'Sí' : 'No';
    if (field.field_type === 'date') return new Date(String(value)).toLocaleDateString('es-CO');
    return String(value);
  }

  formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }
}
