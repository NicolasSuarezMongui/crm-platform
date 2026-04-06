import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ObjectTypesService } from '../../../core/services/object-type.service';
import { AuthService } from '../../../core/services/auth.service';
import { ObjectTypeSummary } from '../../../core/models/objects.models';

@Component({
  selector: 'app-object-types-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './object-types-list.component.html',
})
export class ObjectTypesListComponent implements OnInit {
  private readonly service = inject(ObjectTypesService);
  protected readonly auth = inject(AuthService);

  readonly objectTypes = signal<ObjectTypeSummary[]>([]);
  readonly loading = signal(true);

  ngOnInit(): void {
    this.service.list().subscribe({
      next: (types) => {
        this.objectTypes.set(types);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}
