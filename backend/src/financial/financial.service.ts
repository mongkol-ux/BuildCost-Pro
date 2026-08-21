import { Injectable } from '@nestjs/common';
import { FinancialRepository } from './financial.repository';

@Injectable()
export class FinancialService {
  constructor(private readonly repo: FinancialRepository) {}
  transactions(projectId: string) { return this.repo.listTransactions(projectId); }
  createTransaction(input: any) { return this.repo.createTransaction(input); }
  costs(projectId: string) { return this.repo.listCosts(projectId); }
  createCost(input: any) { return this.repo.createCost({ ...input, total: Number(input.quantity) * Number(input.unitCost) }); }
  budgets(projectId: string) { return this.repo.listBudgets(projectId); }
  createBudget(input: any) { return this.repo.createBudget(input); }
}
