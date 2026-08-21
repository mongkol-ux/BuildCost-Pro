import { Injectable, NotFoundException } from '@nestjs/common';
import { ProjectRepository } from './project.repository';

@Injectable()
export class ProjectService {
  constructor(private readonly repo: ProjectRepository) {}
  list() { return this.repo.findAll(); }
  async get(id: string) { const project = await this.repo.findById(id); if (!project) throw new NotFoundException('Project not found'); return project; }
  create(input: { code: string; name: string; description?: string }) { return this.repo.create(input); }
  async update(id: string, input: { name?: string; description?: string; status?: any }) { await this.get(id); return this.repo.update(id, input); }
}
