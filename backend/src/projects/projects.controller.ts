import { Body, Controller, Get, Param, Patch, Post } from '@nestjs/common';
import { ProjectService } from './project.service';

@Controller('api/v1/projects')
export class ProjectsController {
  constructor(private readonly service: ProjectService) {}
  @Get() list() { return this.service.list(); }
  @Get(':id') get(@Param('id') id: string) { return this.service.get(id); }
  @Post() create(@Body() body: { code: string; name: string; description?: string }) { return this.service.create(body); }
  @Patch(':id') update(@Param('id') id: string, @Body() body: any) { return this.service.update(id, body); }
}
