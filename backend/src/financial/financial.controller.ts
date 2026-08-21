import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { FinancialService } from './financial.service';

@Controller('api/v1/projects/:projectId')
export class FinancialController {
  constructor(private readonly service: FinancialService) {}
  @Get('transactions') transactions(@Param('projectId') id: string) { return this.service.transactions(id); }
  @Post('transactions') createTransaction(@Param('projectId') projectId: string, @Body() body: any) { return this.service.createTransaction({ ...body, projectId }); }
  @Get('costs') costs(@Param('projectId') id: string) { return this.service.costs(id); }
  @Post('costs') createCost(@Param('projectId') projectId: string, @Body() body: any) { return this.service.createCost({ ...body, projectId }); }
  @Get('budgets') budgets(@Param('projectId') id: string) { return this.service.budgets(id); }
  @Post('budgets') createBudget(@Param('projectId') projectId: string, @Body() body: any) { return this.service.createBudget({ ...body, projectId }); }
}
