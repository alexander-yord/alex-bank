-- product categories
insert into `product_categories` (`category_id`, `category_name`, `description`)
values 
	('LON', 'Loan', 'Loans are agreements in which Alex Bank lends money out to the loan applicant in exchange for an interest.'), 
    ('PEQ', 'Private Equity Offerring', 'Private Equity Offerings involve the sale of private equity, facilitated by Alex Bank.'), 
    ('DER', 'Exotic Derivative', 'Instruments whose price depends on the performance of some underlying asset or condition.');
 
-- product subcategories
INSERT INTO product_subcategories (category_id, subcategory_name, subcategory_description) VALUES
('DER', 'Futures Contract', 'A financial contract which compels the exchange of the underlying on the exercise date.'),
('DER', 'European Option', 'A financial derivative that can only be exercised at expiration.'),
('DER', 'American Option', 'A financial derivative that can be exercised at any time before or on its expiration date.'),
('DER', 'Bermudan Option', 'A financial derivative that can be exercised at specific dates before expiration.'),
('DER', 'Asian Option', 'A financial derivative whose payoff depends on the average price of the underlying asset over a set period.'),
('DER', 'Basket Option', 'A financial derivative based on the value of a weighted portfolio of multiple underlying assets.'),
('DER', 'Range Option', 'A financial derivative that provides a payoff if the underlying asset\'s price stays within a predetermined range during a specified period.');


-- products Small and Medium Short-Term BGN Loans
insert into `products` (`category_id`, `name`, `description`, `terms_and_conditions`, 
`currency`, `term`, `percentage`, `monetary_amount`, `percentage_label`, `mon_amt_label`, `available_from`, `available_till`)
values 
	('LON', 'Small 1-Month Loan',  'Loan of less than BGN 100 with term of 1 month', '<ol>
    <li>Introduction
        <p>These Terms and Conditions ("Agreement") govern the issuance of a Small 1-Month ("Loan") by Alex Bank ("Lender") to the borrower ("Borrower"). By applying for the Loan, the Borrower agrees to comply with these terms and conditions.</p>
    </li>
    <li>Loan Amount and Disbursement
        <ul>
            <li><strong>Loan Amount</strong>: The principal amount of the Loan shall be that agreed to by the Lender and the Borrower, but, in general, shall not exceed BGN100.00.</li>
            <li><strong>Disbursement Date</strong>: The Loan shall be disbursed to the Borrower\'s designated account within one business day of signing the contract, unless a disbursement date has otherwise been agreed upon.</li>
        </ul>
    </li>
    <li>Interest Rate and Fees
        <ul>
            <li><strong>Interest Rate</strong>: The Loan shall bear interest at the rate of 1.00% per month.</li>
            <li><strong>Late Payment Fee</strong>: A late payment fee of 0.5% of the overdue amount (overdue amount = principal amount + accumulated interest + unpaid fees) will be charged for each day the amount is not paid after the first week after the due date.</li>
        </ul>
    </li>
    <li>Repayment Terms
        The Loan shall be repaid on the day it is due or no later than one week thereafter. 
    </li>
    <li>Prepayment
	The Borrower may prepay the Loan in full (its principal amount and the <i>pro rata</i> interest) at any time without penalty.
    </li>
    <li>Default
        <ul>
            <li><strong>Events of Default</strong>: The Loan shall be considered in default if the Borrower fails to make the payment on the due date, or if the Borrower breaches any other terms of this Agreement.</li>
            <li><strong>Consequences of Default</strong>: In the event of default, the Lender may demand immediate repayment of the entire outstanding Loan amount, including accrued interest and fees.</li>
        </ul>
    </li>
    <li>Borrower Representations and Warranties
        <ul>
            <li>The Borrower represents and warrants that all information provided in the Loan application is true and accurate.</li>
            <li>The Borrower agrees to notify the Lender promptly of any changes to their contact information or financial status.</li>
        </ul>
    </li>
    <li>Miscellaneous
        <ul>
            <li><strong>Amendments</strong>: Any amendments to this Agreement must be in writing and signed by both the Borrower and the Lender.</li>
            <li><strong>Severability</strong>: If any provision of this Agreement is found to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.</li>
            <li><strong>Entire Agreement</strong>: This Agreement constitutes the entire agreement between the Borrower and the Lender regarding the Loan and supersedes all prior agreements and understandings.</li>
        </ul>
    </li>
    <li>Contact Information
        <ul>
            <li><strong>Lender Contact Information</strong>: For any inquiries or notifications, the Borrower may contact the Lender at <a href="mailto:smpt.alex.bank.com@gmail.com">smpt.alex.bank.com@gmail.com</a></li>
        </ul>
    </li>
</ol>
<p>By accepting the Loan, the Borrower acknowledges that they have read, understood, and agreed to these Terms and Conditions.</p>', 'BGN', 1, 0.0000, 100.0, 'Interest rate', 'Maximum amount', '2024-05-25', NULL), 
	('LON', 'Small 3-Month Loan',  'Loan of less than BGN 100 with term of 3 month', '<ol>
   <li>
      Introduction         
      <p>These Terms and Conditions ("Agreement") govern the issuance of a Small 3-Month Loan ("Loan") by Alex Bank ("Lender") to the borrower ("Borrower"). By applying for the Loan, the Borrower agrees to comply with these terms and conditions.</p>
   </li>
   <li>
      Loan Amount and Disbursement         
      <ul>
         <li><strong>Loan Amount</strong>: The principal amount of the Loan shall be that agreed to by the Lender and the Borrower, but, in general, shall not exceed BGN100.00.</li>
         <li><strong>Disbursement Date</strong>: The Loan shall be disbursed to the Borrower\'s designated account within one business day of signing the contract, unless a disbursement date has otherwise been agreed upon.</li>
      </ul>
   </li>
   <li>
      Interest Rate and Fees         
      <ul>
         <li><strong>Interest Rate</strong>: The Loan shall bear interest at the rate of 1.00% per month.</li>
         <li><strong>Late Payment Fee</strong>: A late payment fee of 0.5% of the overdue amount (overdue amount = principal amount + accumulated interest + unpaid fees) will be charged for each day the amount is not paid after the first week after the due date.</li>
      </ul>
   </li>
   <li>Repayment Terms         The Loan shall be repaid on the day it is due or no later than one week thereafter.      </li>
   <li>Prepayment 	The Borrower may prepay the Loan in full (its principal amount and the <i>pro rata</i> interest) at any time without penalty.     </li>
   <li>
      Default         
      <ul>
         <li><strong>Events of Default</strong>: The Loan shall be considered in default if the Borrower fails to make the payment on the due date, or if the Borrower breaches any other terms of this Agreement.</li>
         <li><strong>Consequences of Default</strong>: In the event of default, the Lender may demand immediate repayment of the entire outstanding Loan amount, including accrued interest and fees.</li>
      </ul>
   </li>
   <li>
      Borrower Representations and Warranties         
      <ul>
         <li>The Borrower represents and warrants that all information provided in the Loan application is true and accurate.</li>
         <li>The Borrower agrees to notify the Lender promptly of any changes to their contact information or financial status.</li>
      </ul>
   </li>
   <li>
      Miscellaneous         
      <ul>
         <li><strong>Amendments</strong>: Any amendments to this Agreement must be in writing and signed by both the Borrower and the Lender.</li>
         <li><strong>Severability</strong>: If any provision of this Agreement is found to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.</li>
         <li><strong>Entire Agreement</strong>: This Agreement constitutes the entire agreement between the Borrower and the Lender regarding the Loan and supersedes all prior agreements and understandings.</li>
      </ul>
   </li>
   <li>
      Contact Information         
      <ul>
         <li><strong>Lender Contact Information</strong>: For any inquiries or notifications, the Borrower may contact the Lender at <a href="mailto:smpt.alex.bank.com@gmail.com">smpt.alex.bank.com@gmail.com</a></li>
      </ul>
   </li>
</ol>
<p>By accepting the Loan, the Borrower acknowledges that they have read, understood, and agreed to these Terms and Conditions.</p>', 'BGN', 3, 0.0100, 100.0, 'Interest rate', 'Maximum amount', '2024-05-25', NULL), 
    ('LON', 'Medium 1-Month Loan', 'Loan of less than BGN 500 with term of 1 month', '<ol>
   <li>
      Introduction         
      <p>These Terms and Conditions ("Agreement") govern the issuance of a Medium 1-Month Loan ("Loan") by Alex Bank ("Lender") to the borrower ("Borrower"). By applying for the Loan, the Borrower agrees to comply with these terms and conditions.</p>
   </li>
   <li>
      Loan Amount and Disbursement         
      <ul>
         <li><strong>Loan Amount</strong>: The principal amount of the Loan shall be that agreed to by the Lender and the Borrower, but, in general, shall not exceed BGN500.00.</li>
         <li><strong>Disbursement Date</strong>: The Loan shall be disbursed to the Borrower\'s designated account within one business day of signing the contract, unless a disbursement date has otherwise been agreed upon.</li>
      </ul>
   </li>
   <li>
      Interest Rate and Fees         
      <ul>
         <li><strong>Interest Rate</strong>: The Loan shall bear interest at the rate of 1.00% per month.</li>
         <li><strong>Late Payment Fee</strong>: A late payment fee of 0.5% of the overdue amount (overdue amount = principal amount + accumulated interest + unpaid fees) will be charged for each day the amount is not paid after the first week after the due date.</li>
      </ul>
   </li>
   <li>Repayment Terms         The Loan shall be repaid on the day it is due or no later than one week thereafter.      </li>
   <li>Prepayment 	The Borrower may prepay the Loan in full (its principal amount and the <i>pro rata</i> interest) at any time without penalty.     </li>
   <li>
      Default         
      <ul>
         <li><strong>Events of Default</strong>: The Loan shall be considered in default if the Borrower fails to make the payment on the due date, or if the Borrower breaches any other terms of this Agreement.</li>
         <li><strong>Consequences of Default</strong>: In the event of default, the Lender may demand immediate repayment of the entire outstanding Loan amount, including accrued interest and fees.</li>
      </ul>
   </li>
   <li>
      Borrower Representations and Warranties         
      <ul>
         <li>The Borrower represents and warrants that all information provided in the Loan application is true and accurate.</li>
         <li>The Borrower agrees to notify the Lender promptly of any changes to their contact information or financial status.</li>
      </ul>
   </li>
   <li>
      Miscellaneous         
      <ul>
         <li><strong>Amendments</strong>: Any amendments to this Agreement must be in writing and signed by both the Borrower and the Lender.</li>
         <li><strong>Severability</strong>: If any provision of this Agreement is found to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.</li>
         <li><strong>Entire Agreement</strong>: This Agreement constitutes the entire agreement between the Borrower and the Lender regarding the Loan and supersedes all prior agreements and understandings.</li>
      </ul>
   </li>
   <li>
      Contact Information         
      <ul>
         <li><strong>Lender Contact Information</strong>: For any inquiries or notifications, the Borrower may contact the Lender at <a href="mailto:smpt.alex.bank.com@gmail.com">smpt.alex.bank.com@gmail.com</a></li>
      </ul>
   </li>
</ol>
<p>By accepting the Loan, the Borrower acknowledges that they have read, understood, and agreed to these Terms and Conditions.</p>', 'BGN', 1, 0.0100, 500.0, 'Interest rate', 'Maximum amount', '2024-05-25', NULL), 
    ('LON', 'Medium 3-Month Loan', 'Loan of less than BGN 500 with term of 3 month', '<ol>
   <li>
      Introduction         
      <p>These Terms and Conditions ("Agreement") govern the issuance of a Medium 3-Month Loan ("Loan") by Alex Bank ("Lender") to the borrower ("Borrower"). By applying for the Loan, the Borrower agrees to comply with these terms and conditions.</p>
   </li>
   <li>
      Loan Amount and Disbursement         
      <ul>
         <li><strong>Loan Amount</strong>: The principal amount of the Loan shall be that agreed to by the Lender and the Borrower, but, in general, shall not exceed BGN500.00.</li>
         <li><strong>Disbursement Date</strong>: The Loan shall be disbursed to the Borrower\'s designated account within one business day of signing the contract, unless a disbursement date has otherwise been agreed upon.</li>
      </ul>
   </li>
   <li>
      Interest Rate and Fees         
      <ul>
         <li><strong>Interest Rate</strong>: The Loan shall bear interest at the rate of 1.00% per month.</li>
         <li><strong>Late Payment Fee</strong>: A late payment fee of 0.5% of the overdue amount (overdue amount = principal amount + accumulated interest + unpaid fees) will be charged for each day the amount is not paid after the first week after the due date.</li>
      </ul>
   </li>
   <li>Repayment Terms         The Loan shall be repaid on the day it is due or no later than one week thereafter.      </li>
   <li>Prepayment 	The Borrower may prepay the Loan in full (its principal amount and the <i>pro rata</i> interest) at any time without penalty.     </li>
   <li>
      Default         
      <ul>
         <li><strong>Events of Default</strong>: The Loan shall be considered in default if the Borrower fails to make the payment on the due date, or if the Borrower breaches any other terms of this Agreement.</li>
         <li><strong>Consequences of Default</strong>: In the event of default, the Lender may demand immediate repayment of the entire outstanding Loan amount, including accrued interest and fees.</li>
      </ul>
   </li>
   <li>
      Borrower Representations and Warranties         
      <ul>
         <li>The Borrower represents and warrants that all information provided in the Loan application is true and accurate.</li>
         <li>The Borrower agrees to notify the Lender promptly of any changes to their contact information or financial status.</li>
      </ul>
   </li>
   <li>
      Miscellaneous         
      <ul>
         <li><strong>Amendments</strong>: Any amendments to this Agreement must be in writing and signed by both the Borrower and the Lender.</li>
         <li><strong>Severability</strong>: If any provision of this Agreement is found to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.</li>
         <li><strong>Entire Agreement</strong>: This Agreement constitutes the entire agreement between the Borrower and the Lender regarding the Loan and supersedes all prior agreements and understandings.</li>
      </ul>
   </li>
   <li>
      Contact Information         
      <ul>
         <li><strong>Lender Contact Information</strong>: For any inquiries or notifications, the Borrower may contact the Lender at <a href="mailto:smpt.alex.bank.com@gmail.com">smpt.alex.bank.com@gmail.com</a></li>
      </ul>
   </li>
</ol>
<p>By accepting the Loan, the Borrower acknowledges that they have read, understood, and agreed to these Terms and Conditions.</p>', 'BGN', 3, 0.0200, 500.0, 'Interest rate', 'Maximum amount', '2024-05-25', NULL);
