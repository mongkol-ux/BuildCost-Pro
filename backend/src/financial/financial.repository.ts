import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Prisma, TransactionType } from '@prisma/client';

@Injectable()
export class FinancialRepository {
  constructor(private readonly db: PrismaService) {}
  listTransactions(projectId: string) { return this.db.transaction.findMany({ where: { projectId }, orderBy: { occurredAt: 'desc' } }); }
  createTransaction(data: { projectId: string; type: TransactionType; amount: Prisma.Decimal | number; reference?: string; description?: string }) { return this.db.transaction.create({ data }); }
  listCosts(projectId: string) { return this.db.cost.findMany({ where: { projectId }, orderBy: { occurredAt: 'desc' } }); }
  createCost(data: { projectId: string; category: string; description?: string; quantity: Prisma.Decimal | number; unitCost: Prisma.Decimal | number; total: Prisma.Decimal | number }) { return this.db.cost.create({ data }); }
  listBudgets(projectId: string) { return this.db.budget.findMany({ where: { projectId }, orderBy: { createdAt: 'desc' } }); }
  createBudget(data: { projectId: string; name: string; amount: Prisma.Decimal | number }) { return this.db.budget.create({ data }); }
}
