import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { RecordsService } from '../../../core/services/records.service';
import { ObjectTypesService } from '../../../core/services/object-type.service';
import { AuthService } from '../../../core/services/auth.service';
import { CrmRecord, ObjectType } from '../../../core/models/objects.models';
import { FieldInputComponent } from '../../../shared/components/field-input/field-input.component';

@Component({
  selector: 'app-record-detail',
  standalone: true,
  imports: [RouterLink, FieldInputComponent],
  templateUrl: './record-detail.component.html',
})
export class RecordDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly recordsService = inject(RecordsService);
  private readonly objectTypesService = inject(ObjectTypesService);
  protected readonly auth = inject(AuthService);

  readonly record = signal<CrmRecord | null>(null);
  readonly objectType = signal<ObjectType | null>(null);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly deleting = signal(false);
  readonly saveError = signal<string | null>(null);
  readonly saveSuccess = signal(false);
  readonly showDeleteConfirm = signal(false);

  readonly editName = signal('');
  readonly editData = signal<Record<string, unknown>>({});
  readonly fieldErrors = signal<Record<string, string>>({});

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    const objectTypeParam = this.route.snapshot.queryParamMap.get('object_type');

    this.recordsService.getById(id).subscribe({
      next: (rec) => {
        this.record.set(rec);
        this.editName.set(rec.name);
        this.editData.set({ ...rec.data });
        this.loading.set(false);

        // Load object type for field definitions
        const apiName = objectTypeParam;
        if (apiName) {
          this.objectTypesService.list().subscribe((types) => {
            const summary = types.find((t) => t.api_name === apiName);
            if (summary) {
              this.objectTypesService.getById(summary.id).subscribe((full) => {
                this.objectType.set(full);
              });
            }
          });
        }
      },
      error: () => this.router.navigate(['/dashboard']),
    });
  }

  updateField(apiName: string, value: unknown): void {
    this.editData.update((d) => ({ ...d, [apiName]: value }));
  }

  save(): void {
    if (!this.editName().trim() || !this.record()) return;
    this.saving.set(true);
    this.saveError.set(null);
    this.fieldErrors.set({});

    this.recordsService
      .update(this.record()!.id, {
        name: this.editName(),
        data: this.editData(),
      })
      .subscribe({
        next: (rec) => {
          this.record.set(rec);
          this.saving.set(false);
          this.saveSuccess.set(true);
          setTimeout(() => this.saveSuccess.set(false), 3000);
        },
        error: (err) => {
          this.saving.set(false);
          const detail = err?.error?.detail;
          if (detail?.errors) {
            this.fieldErrors.set(detail.errors);
          } else {
            this.saveError.set(detail?.message ?? 'Error al guardar');
          }
        },
      });
  }

  confirmDelete(): void {
    this.showDeleteConfirm.set(true);
  }

  deleteRecord(): void {
    if (!this.record()) return;
    this.deleting.set(true);
    this.recordsService.delete(this.record()!.id).subscribe({
      next: () => {
        this.router.navigate(['/records', this.objectType()?.api_name ?? '']);
      },
      error: () => this.deleting.set(false),
    });
  }

  formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  }
}
