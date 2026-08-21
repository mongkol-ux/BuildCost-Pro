import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class ProjectRepository {
  constructor(private readonly db: PrismaService) {}
  findAll() { return this.db.project.findMany({ orderBy: { createdAt: 'desc' } }); }
  findById(id: string) { return this.db.project.findUnique({ where: { id }, include: { budgets: true } }); }
  create(data: { code: string; name: string; description?: string }) { return this.db.project.create({ data }); }
  update(id: string, data: { name?: string; description?: string; status?: any }) { return this.db.project.update({ where: { id }, data }); }
}
