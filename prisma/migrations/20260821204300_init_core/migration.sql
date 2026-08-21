CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE "UserStatus" AS ENUM ('ACTIVE','INACTIVE','SUSPENDED');
CREATE TYPE "ProjectStatus" AS ENUM ('DRAFT','ACTIVE','ON_HOLD','COMPLETED','CANCELLED');
CREATE TYPE "TransactionType" AS ENUM ('INCOME','EXPENSE','TRANSFER');
CREATE TYPE "TransactionStatus" AS ENUM ('DRAFT','POSTED','VOIDED');
CREATE TYPE "PaymentStatus" AS ENUM ('PENDING','PARTIAL','PAID','CANCELLED');
CREATE TYPE "CostCategoryType" AS ENUM ('MATERIAL','LABOR','EQUIPMENT','SUBCONTRACT','FUEL','OTHER');
CREATE TYPE "EvidenceType" AS ENUM ('NONE','RECEIPT','INVOICE','TAX_INVOICE','QUOTATION','CONTRACT','PHOTO','OTHER');
CREATE TYPE "ApprovalStatus" AS ENUM ('PENDING','APPROVED','REJECTED');
CREATE TYPE "DocumentType" AS ENUM ('RECEIPT','INVOICE','TAX_INVOICE','CONTRACT','QUOTATION','BOQ','OTHER');

CREATE TABLE "Company" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "code" VARCHAR(50) NOT NULL, "name" VARCHAR(200) NOT NULL,
  "taxId" VARCHAR(50), "phone" VARCHAR(50), "email" VARCHAR(150), "address" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Company_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Company_code_key" ON "Company"("code");

CREATE TABLE "User" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "email" VARCHAR(150) NOT NULL,
  "passwordHash" TEXT NOT NULL, "firstName" VARCHAR(100) NOT NULL, "lastName" VARCHAR(100) NOT NULL,
  "status" "UserStatus" NOT NULL DEFAULT 'ACTIVE', "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL, CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "User_email_key" ON "User"("email"); CREATE INDEX "User_companyId_idx" ON "User"("companyId");

CREATE TABLE "Customer" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "code" VARCHAR(50) NOT NULL,
  "name" VARCHAR(200) NOT NULL, "taxId" VARCHAR(50), "phone" VARCHAR(50), "email" VARCHAR(150),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Customer_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Customer_companyId_code_key" ON "Customer"("companyId","code"); CREATE INDEX "Customer_companyId_name_idx" ON "Customer"("companyId","name");

CREATE TABLE "Supplier" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "code" VARCHAR(50) NOT NULL,
  "name" VARCHAR(200) NOT NULL, "taxId" VARCHAR(50), "phone" VARCHAR(50), "email" VARCHAR(150),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Supplier_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Supplier_companyId_code_key" ON "Supplier"("companyId","code"); CREATE INDEX "Supplier_companyId_name_idx" ON "Supplier"("companyId","name");

CREATE TABLE "Project" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "customerId" UUID, "createdById" UUID NOT NULL,
  "code" VARCHAR(50) NOT NULL, "name" VARCHAR(200) NOT NULL, "description" TEXT, "status" "ProjectStatus" NOT NULL DEFAULT 'DRAFT',
  "startDate" DATE, "endDate" DATE, "contractValue" DECIMAL(18,2), "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL, CONSTRAINT "Project_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Project_companyId_code_key" ON "Project"("companyId","code"); CREATE INDEX "Project_companyId_status_idx" ON "Project"("companyId","status");

CREATE TABLE "Category" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "code" VARCHAR(50) NOT NULL,
  "name" VARCHAR(150) NOT NULL, "type" "CostCategoryType" NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL, CONSTRAINT "Category_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Category_companyId_code_key" ON "Category"("companyId","code");

CREATE TABLE "Unit" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "companyId" UUID NOT NULL, "code" VARCHAR(30) NOT NULL,
  "name" VARCHAR(100) NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Unit_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Unit_companyId_code_key" ON "Unit"("companyId","code");

CREATE TABLE "Budget" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "projectId" UUID NOT NULL, "name" VARCHAR(150) NOT NULL,
  "version" INTEGER NOT NULL DEFAULT 1, "total" DECIMAL(18,2) NOT NULL DEFAULT 0, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL, CONSTRAINT "Budget_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Budget_projectId_version_key" ON "Budget"("projectId","version");

CREATE TABLE "BudgetItem" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "budgetId" UUID NOT NULL, "categoryId" UUID,
  "description" VARCHAR(255) NOT NULL, "quantity" DECIMAL(18,4) NOT NULL DEFAULT 1, "unitPrice" DECIMAL(18,2) NOT NULL DEFAULT 0,
  "amount" DECIMAL(18,2) NOT NULL DEFAULT 0, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "BudgetItem_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "BudgetItem_budgetId_idx" ON "BudgetItem"("budgetId");

CREATE TABLE "CostItem" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "projectId" UUID NOT NULL, "categoryId" UUID NOT NULL, "unitId" UUID,
  "description" VARCHAR(255) NOT NULL, "quantity" DECIMAL(18,4) NOT NULL DEFAULT 1, "unitPrice" DECIMAL(18,2) NOT NULL DEFAULT 0,
  "amount" DECIMAL(18,2) NOT NULL DEFAULT 0, "occurredAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "CostItem_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "CostItem_projectId_categoryId_idx" ON "CostItem"("projectId","categoryId");

CREATE TABLE "Transaction" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "projectId" UUID NOT NULL, "userId" UUID NOT NULL, "supplierId" UUID,
  "type" "TransactionType" NOT NULL, "status" "TransactionStatus" NOT NULL DEFAULT 'DRAFT', "paymentStatus" "PaymentStatus" NOT NULL DEFAULT 'PENDING',
  "evidenceType" "EvidenceType" NOT NULL DEFAULT 'NONE', "description" VARCHAR(255) NOT NULL, "referenceNo" VARCHAR(100),
  "transactionAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "subtotal" DECIMAL(18,2) NOT NULL DEFAULT 0,
  "taxAmount" DECIMAL(18,2) NOT NULL DEFAULT 0, "totalAmount" DECIMAL(18,2) NOT NULL DEFAULT 0, "notes" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Transaction_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "Transaction_projectId_transactionAt_idx" ON "Transaction"("projectId","transactionAt"); CREATE INDEX "Transaction_projectId_type_status_idx" ON "Transaction"("projectId","type","status");

CREATE TABLE "TransactionItem" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "transactionId" UUID NOT NULL, "categoryId" UUID,
  "description" VARCHAR(255) NOT NULL, "quantity" DECIMAL(18,4) NOT NULL DEFAULT 1, "unitPrice" DECIMAL(18,2) NOT NULL DEFAULT 0,
  "amount" DECIMAL(18,2) NOT NULL DEFAULT 0, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "TransactionItem_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "TransactionItem_transactionId_idx" ON "TransactionItem"("transactionId");

CREATE TABLE "Payment" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "transactionId" UUID NOT NULL, "amount" DECIMAL(18,2) NOT NULL,
  "paidAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "method" VARCHAR(50), "referenceNo" VARCHAR(100), "notes" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "Payment_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "Payment_transactionId_paidAt_idx" ON "Payment"("transactionId","paidAt");

CREATE TABLE "Document" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "projectId" UUID NOT NULL, "transactionId" UUID, "type" "DocumentType" NOT NULL,
  "fileName" VARCHAR(255) NOT NULL, "storageKey" VARCHAR(500) NOT NULL, "mimeType" VARCHAR(100), "fileSize" BIGINT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "Document_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "Document_projectId_type_idx" ON "Document"("projectId","type");

CREATE TABLE "Approval" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "projectId" UUID NOT NULL, "transactionId" UUID, "approverId" UUID NOT NULL,
  "status" "ApprovalStatus" NOT NULL DEFAULT 'PENDING', "comment" TEXT, "decidedAt" TIMESTAMP(3),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "Approval_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "Approval_projectId_status_idx" ON "Approval"("projectId","status");

CREATE TABLE "AuditLog" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "userId" UUID, "entityType" VARCHAR(80) NOT NULL, "entityId" VARCHAR(80) NOT NULL,
  "action" VARCHAR(50) NOT NULL, "beforeJson" JSONB, "afterJson" JSONB, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "AuditLog_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "AuditLog_entityType_entityId_idx" ON "AuditLog"("entityType","entityId"); CREATE INDEX "AuditLog_createdAt_idx" ON "AuditLog"("createdAt");

ALTER TABLE "User" ADD CONSTRAINT "User_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Customer" ADD CONSTRAINT "Customer_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Supplier" ADD CONSTRAINT "Supplier_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Project" ADD CONSTRAINT "Project_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Project" ADD CONSTRAINT "Project_customerId_fkey" FOREIGN KEY ("customerId") REFERENCES "Customer"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Project" ADD CONSTRAINT "Project_createdById_fkey" FOREIGN KEY ("createdById") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Category" ADD CONSTRAINT "Category_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Unit" ADD CONSTRAINT "Unit_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Budget" ADD CONSTRAINT "Budget_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "BudgetItem" ADD CONSTRAINT "BudgetItem_budgetId_fkey" FOREIGN KEY ("budgetId") REFERENCES "Budget"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "CostItem" ADD CONSTRAINT "CostItem_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "CostItem" ADD CONSTRAINT "CostItem_categoryId_fkey" FOREIGN KEY ("categoryId") REFERENCES "Category"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "CostItem" ADD CONSTRAINT "CostItem_unitId_fkey" FOREIGN KEY ("unitId") REFERENCES "Unit"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Transaction" ADD CONSTRAINT "Transaction_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Transaction" ADD CONSTRAINT "Transaction_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Transaction" ADD CONSTRAINT "Transaction_supplierId_fkey" FOREIGN KEY ("supplierId") REFERENCES "Supplier"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "TransactionItem" ADD CONSTRAINT "TransactionItem_transactionId_fkey" FOREIGN KEY ("transactionId") REFERENCES "Transaction"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Payment" ADD CONSTRAINT "Payment_transactionId_fkey" FOREIGN KEY ("transactionId") REFERENCES "Transaction"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Document" ADD CONSTRAINT "Document_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Document" ADD CONSTRAINT "Document_transactionId_fkey" FOREIGN KEY ("transactionId") REFERENCES "Transaction"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Approval" ADD CONSTRAINT "Approval_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Approval" ADD CONSTRAINT "Approval_transactionId_fkey" FOREIGN KEY ("transactionId") REFERENCES "Transaction"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Approval" ADD CONSTRAINT "Approval_approverId_fkey" FOREIGN KEY ("approverId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "AuditLog" ADD CONSTRAINT "AuditLog_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
