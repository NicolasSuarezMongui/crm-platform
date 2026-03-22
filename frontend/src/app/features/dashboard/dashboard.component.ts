import { Component, inject } from '@angular/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent {
  protected readonly auth = inject(AuthService);

  readonly cards = [
    { label: 'Usuarios activos', value: '—' },
    { label: 'Roles configurados', value: '—' },
    { label: 'Registros totales', value: '—' },
  ];
}
