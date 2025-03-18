import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MiPrimeraPaginaComponent } from './mi-primera-pagina.component';

describe('MiPrimeraPaginaComponent', () => {
  let component: MiPrimeraPaginaComponent;
  let fixture: ComponentFixture<MiPrimeraPaginaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MiPrimeraPaginaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MiPrimeraPaginaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
