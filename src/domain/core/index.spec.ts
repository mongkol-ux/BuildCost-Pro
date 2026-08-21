import { CostLine, Money, Project, ProjectFinancials, TransactionAggregate } from './index';

describe('Money', () => {
  it('calculates with decimal-safe rounding', () => {
    expect(Money.of(10.105).add(Money.of(0.005)).amount).toBe(10.12);
  });
});

describe('Project', () => {
  it('starts as draft and can be activated', () => {
    const project = new Project({ id: 'p1', companyId: 'c1', code: 'P-001', name: 'Demo', createdById: 'u1' });
    expect(project.status).toBe('DRAFT');
    project.activate();
    expect(project.status).toBe('ACTIVE');
  });
});

describe('TransactionAggregate', () => {
  it('computes subtotal and total and requires an item before posting', () => {
    const tx = new TransactionAggregate({ id: 't1', projectId: 'p1', userId: 'u1', type: 'EXPENSE', description: 'Cement' });
    const line = new CostLine({ id: 'l1', categoryId: 'cat1', description: 'Cement', quantity: 10, unitPrice: Money.of(25) });
    tx.addItem(line);
    tx.setTax(Money.of(17.5));
    expect(tx.subtotal.amount).toBe(250);
    expect(tx.totalAmount.amount).toBe(267.5);
    tx.post();
    expect(tx.status).toBe('POSTED');
  });
});

describe('ProjectFinancials', () => {
  it('calculates profit and remaining budget', () => {
    const income = Money.of(1000);
    const expense = Money.of(600);
    expect(ProjectFinancials.profit({ contractValue: Money.of(1000), income, expense, budget: Money.of(800), actualCost: Money.of(600) }).amount).toBe(400);
    expect(ProjectFinancials.budgetVariance({ contractValue: Money.of(1000), income, expense, budget: Money.of(800), actualCost: Money.of(600) }).amount).toBe(200);
  });
});
