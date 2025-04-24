use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token};

declare_id!("your_program_id");

#[program]
pub mod genome_program {
    use super::*;

    pub fn initialize_genome(
        ctx: Context<InitializeGenome>,
        storage_id: String,
        metadata: String,
    ) -> Result<()> {
        let genome = &mut ctx.accounts.genome;
        let user = &ctx.accounts.user;

        genome.storage_id = storage_id;
        genome.metadata = metadata;
        genome.owner = user.key();
        genome.created_at = Clock::get()?.unix_timestamp;
        genome.deleted = false;

        Ok(())
    }

    pub fn create_transaction(
        ctx: Context<CreateTransaction>,
        genome_id: String,
        price: u64,
        duration: i64,
    ) -> Result<()> {
        let transaction = &mut ctx.accounts.transaction;
        let user = &ctx.accounts.user;

        transaction.genome_id = genome_id;
        transaction.seller = user.key();
        transaction.price = price;
        transaction.duration = duration;
        transaction.status = TransactionStatus::Created;
        transaction.created_at = Clock::get()?.unix_timestamp;

        Ok(())
    }

    pub fn execute_transaction(ctx: Context<ExecuteTransaction>) -> Result<()> {
        let transaction = &mut ctx.accounts.transaction;
        let buyer = &ctx.accounts.buyer;

        require!(
            transaction.status == TransactionStatus::Created,
            GenomeError::InvalidTransactionStatus
        );

        transaction.buyer = Some(buyer.key());
        transaction.status = TransactionStatus::Executed;
        transaction.executed_at = Some(Clock::get()?.unix_timestamp);

        Ok(())
    }

    pub fn cancel_transaction(ctx: Context<CancelTransaction>) -> Result<()> {
        let transaction = &mut ctx.accounts.transaction;
        
        require!(
            transaction.status == TransactionStatus::Created,
            GenomeError::InvalidTransactionStatus
        );

        transaction.status = TransactionStatus::Cancelled;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeGenome<'info> {
    #[account(init, payer = user, space = 1000)]
    pub genome: Account<'info, Genome>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CreateTransaction<'info> {
    #[account(init, payer = user, space = 1000)]
    pub transaction: Account<'info, Transaction>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteTransaction<'info> {
    #[account(mut)]
    pub transaction: Account<'info, Transaction>,
    pub buyer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CancelTransaction<'info> {
    #[account(mut)]
    pub transaction: Account<'info, Transaction>,
    pub authority: Signer<'info>,
}

#[account]
pub struct Genome {
    pub storage_id: String,
    pub metadata: String,
    pub owner: Pubkey,
    pub created_at: i64,
    pub deleted: bool,
}

#[account]
pub struct Transaction {
    pub genome_id: String,
    pub seller: Pubkey,
    pub buyer: Option<Pubkey>,
    pub price: u64,
    pub duration: i64,
    pub status: TransactionStatus,
    pub created_at: i64,
    pub executed_at: Option<i64>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum TransactionStatus {
    Created,
    Executed,
    Cancelled,
}

#[error_code]
pub enum GenomeError {
    #[msg("Invalid transaction status")]
    InvalidTransactionStatus,
} 