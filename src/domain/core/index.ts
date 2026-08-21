export type UUID = string;

export type ProjectStatus = 'DRAFT' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type TransactionType = 'INCOME' | 'EXPENSE' | 'TRANSFER';
export type TransactionStatus = 'DRAFT' | 'POSTED' | 'VOIDED';
export type EvidenceType = 'NONE' | 'RECEIPT' | 'INVOICE' | 'TAX_INVOICE' | 'QUOTATION' | 'CONTRACT' | 'PHOTO' | 'OTHER';
export type CostCategoryType = 'MATERIAL' | 'LABOR' | 'EQUIPMENT' | 'SUBCONTRACT' | 'FUEL' | 'OTHER';

export class Money {
  private constructor(readonly amount: number, readonly currency = 'THB') {
    if (!Number.isFinite(amount)) throw new Error('Money amount must be finite');
    if (amount < 0) throw new Error('Money amount cannot be negative');
  }

  static zero(currency = 'THB'): Money { return new Money(0, currency); }
  static of(amount: number, currency = 'THB'): Money { return new Money(Math.round(amount * 100) / 100, currency); }
  add(other: Money): Money { this.assertCurrency(other); return Money.of(this.amount + other.amount, this.currency); }
  subtract(other: Money): Money { this.assertCurrency(other); if (this.amount < other.amount) throw new Error('Money result cannot be negative'); return Money.of(this.amount - other.amount, this.currency); }
  multiply(quantity: number): Money { if (!Number.isFinite(quantity) || quantity < 0) throw new Error('Invalid quantity'); return Money.of(this.amount * quantity, this.currency); }
  isZero(): boolean { return this.amount === 0; }
  private assertCurrency(other: Money): void { if (this.currency !== other.currency) throw new Error('Currency mismatch'); }
}

export interface CostLineProps {
  id: UUID;
  categoryId: UUID;
  description: string;
  quantity: number;
  unitPrice: Money;
}

export class CostLine {
  readonly id: UUID;
  readonly categoryId: UUID;
  readonly description: string;
  readonly quantity: number;
  readonly unitPrice: Money;

  constructor(props: CostLineProps) {
    if (!props.description.trim()) throw new Error('Cost line description is required');
    if (!Number.isFinite(props.quantity) || props.quantity <= 0) throw new Error('Cost line quantity must be greater than zero');
    this.id = props.id; this.categoryId = props.categoryId; this.description = props.description.trim();
    this.quantity = props.quantity; this.unitPrice = props.unitPrice;
  }

  get amount(): Money { return this.unitPrice.multiply(this.quantity); }
}

export interface ProjectProps {
  id: UUID; companyId: UUID; code: string; name: string; createdById: UUID;
  customerId?: UUID; status?: ProjectStatus; contractValue?: Money;
  startDate?: Date; endDate?: Date;
}

export class Project {
  private _status: ProjectStatus;
  private _contractValue?: Money;

  constructor(private readonly props: ProjectProps) {
    if (!props.code.trim()) throw new Error('Project code is required');
    if (!props.name.trim()) throw new Error('Project name is required');
    this._status = props.status ?? 'DRAFT';
    this._contractValue = props.contractValue;
  }

  get id(): UUID { return this.props.id; }
  get companyId(): UUID { return this.props.companyId; }
  get code(): string { return this.props.code; }
  get name(): string { return this.props.name; }
  get status(): ProjectStatus { return this._status; }
  get contractValue(): Money | undefined { return this._contractValue; }

  activate(): void {
    if (this._status === 'COMPLETED' || this._status === 'CANCELLED') throw new Error('Closed project cannot be activated');
    this._status = 'ACTIVE';
  }

  hold(): void { if (this._status !== 'ACTIVE') throw new Error('Only active project can be put on hold'); this._status = 'ON_HOLD'; }
  complete(): void { if (this._status !== 'ACTIVE' && this._status !== 'ON_HOLD') throw new Error('Project must be active or on hold'); this._status = 'COMPLETED'; }
  cancel(): void { if (this._status === 'COMPLETED') throw new Error('Completed project cannot be cancelled'); this._status = 'CANCELLED'; }
  setContractValue(value: Money): void { if (this._status === 'COMPLETED') throw new Error('Completed project contract value is immutable'); this._contractValue = value; }
}

export interface TransactionProps {
  id: UUID; projectId: UUID; userId: UUID; type: TransactionType;
  description: string; evidenceType?: EvidenceType; transactionAt?: Date;
}

export class TransactionAggregate {
  private readonly lines: CostLine[] = [];
  private _status: TransactionStatus = 'DRAFT';
  private _taxAmount = Money.zero();

  constructor(private readonly props: TransactionProps) {
    if (!props.description.trim()) throw new Error('Transaction description is required');
  }

  get id(): UUID { return this.props.id; }
  get projectId(): UUID { return this.props.projectId; }
  get type(): TransactionType { return this.props.type; }
  get status(): TransactionStatus { return this._status; }
  get evidenceType(): EvidenceType { return this.props.evidenceType ?? 'NONE'; }
  get items(): readonly CostLine[] { return this.lines; }

  addItem(item: CostLine): void {
    if (this._status !== 'DRAFT') throw new Error('Only draft transaction can be edited');
    this.lines.push(item);
  }

  removeItem(itemId: UUID): void {
    if (this._status !== 'DRAFT') throw new Error('Only draft transaction can be edited');
    const index = this.lines.findIndex((x) => x.id === itemId);
    if (index < 0) throw new Error('Transaction item not found');
    this.lines.splice(index, 1);
  }

  setTax(amount: Money): void {
    if (this._status !== 'DRAFT') throw new Error('Only draft transaction can be edited');
    this._taxAmount = amount;
  }

  get subtotal(): Money { return this.lines.reduce((sum, line) => sum.add(line.amount), Money.zero()); }
  get taxAmount(): Money { return this._taxAmount; }
  get totalAmount(): Money { return this.subtotal.add(this._taxAmount); }

  post(): void {
    if (this._status !== 'DRAFT') throw new Error('Only draft transaction can be posted');
    if (this.lines.length === 0) throw new Error('Transaction must contain at least one item');
    this._status = 'POSTED';
  }

  void(): void { if (this._status !== 'POSTED') throw new Error('Only posted transaction can be voided'); this._status = 'VOIDED'; }
}

export interface ProjectFinancialSnapshot {
  contractValue: Money;
  income: Money;
  expense: Money;
  budget: Money;
  actualCost: Money;
}

export class ProjectFinancials {
  static profit(snapshot: ProjectFinancialSnapshot): Money {
    return snapshot.income.subtract(snapshot.expense);
  }

  static budgetVariance(snapshot: ProjectFinancialSnapshot): Money {
    if (snapshot.actualCost.amount >= snapshot.budget.amount) return Money.zero(snapshot.budget.currency);
    return snapshot.budget.subtract(snapshot.actualCost);
  }
}
