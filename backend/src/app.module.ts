import { Module } from '@nestjs/common';
import { PrismaService } from './prisma/prisma.service';
import { ProjectRepository } from './projects/project.repository';
import { ProjectService } from './projects/project.service';
import { ProjectsController } from './projects/projects.controller';
import { FinancialRepository } from './financial/financial.repository';
import { FinancialService } from './financial/financial.service';
import { FinancialController } from './financial/financial.controller';

@Module({
  controllers: [ProjectsController, FinancialController],
  providers: [PrismaService, ProjectRepository, ProjectService, FinancialRepository, FinancialService],
})
export class AppModule {}
