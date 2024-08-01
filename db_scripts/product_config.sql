-- product categories
insert into `product_categories` (`category_id`, `category_name`, `description`, `catalog_yn`)
values 
	('LON', 'Loan', 'Loans are agreements in which Alex Bank lends money out to the loan applicant in exchange for an interest.', 'Y'), 
    ('PEQ', 'Private Equity Offerring', 'Private Equity Offerings involve the sale of private equity, facilitated by Alex Bank.', 'N'), 
    ('DER', 'Exotic Derivative', 'Instruments whose price depends on the performance of some underlying asset or condition.', 'Y');
 
-- product subcategories
INSERT INTO product_subcategories (category_id, subcategory_name, subcategory_description, catalog_yn) VALUES
('DER', 'Futures Contract', 'A financial contract which compels the exchange of the underlying on the exercise date.', 'N'),
('DER', 'European Option', 'A financial derivative that can only be exercised at expiration.', 'Y'),
('DER', 'American Option', 'A financial derivative that can be exercised at any time before or on its expiration date.', 'N'),
('DER', 'Bermudan Option', 'A financial derivative that can be exercised at specific dates before expiration.', 'Y'),
('DER', 'Asian Option', 'A financial derivative whose payoff depends on the average price of the underlying asset over a set period.', 'N'),
('DER', 'Basket Option', 'A financial derivative based on the value of a weighted portfolio of multiple underlying assets.', 'N'),
('DER', 'Range Option', 'A financial derivative that provides a payoff if the underlying asset\'s price stays within a predetermined range during a specified period.', 'N');


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


-- Products Election Polling Derivatives 
insert into products (`category_id`, `subcategory_id`, `name`, `description`, 
`currency`, `term`, `percentage`, `monetary_amount`, `percentage_label`, `mon_amt_label`, `available_from`, `available_till`, `terms_and_conditions`)
values 
('DER', 2, 'European Trump Call (Strike: 3.0%)', 'The poll lead is observed on the strike date, and the Call is exercised if the underlying is higher than the strike', 'BGN', 1, 0.03, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Strike Date:
        <ul>
            <li>The strike date is the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>The underlying poll lead must be higher than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is higher than the strike poll lead on the strike date.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Actual Poll Lead% - Strike Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 2, 'European Trump Call (Strike: 3.5%)', 'The poll lead is observed on the strike date, and the Call is exercised if the underlying is higher than the strike', 'BGN', 1, 0.035, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Strike Date:
        <ul>
            <li>The strike date is the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>The underlying poll lead must be higher than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is higher than the strike poll lead on the strike date.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Actual Poll Lead% - Strike Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 2, 'European Trump Put (Strike: 1.5%)', 'The poll lead is observed on the strike date, and the Call is exercised if the underlying is lower than the strike', 'BGN', 1, 0.015, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Strike Date:
        <ul>
            <li>The strike date is the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>The underlying poll lead must be lower than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the strike date.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Strike Lead% - Actual Poll Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 2, 'European Trump Put (Strike: 1.0%)', 'The poll lead is observed on the strike date, and the Call is exercised if the underlying is lower than the strike', 'BGN', 1, 0.01, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Strike Date:
        <ul>
            <li>The strike date is the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>The underlying poll lead must be lower than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the strike date.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Strike Lead% - Actual Poll Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 4, 'Bermudan Trump Call (Strike: 3.0%)', 'The poll lead is observed on three days and the strike date, and the Call is exercised if the underlying is higher than the strike', 'BGN', 1, 0.03, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Observation & Strike Date:
        <ul>
            <li>The observation and strike dates are the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>There will be three observation dates and one final strike date. All of them will be determined prior to the Product Begin Date. </li>
            <li>The underlying poll lead must be higher than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the observation or strike dates.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Actual Poll Lead% - Strike Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 4, 'Bermudan Trump Call (Strike: 3.5%)', 'The poll lead is observed on three days and the strike date, and the Call is exercised if the underlying is higher than the strike', 'BGN', 1, 0.035, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Observation & Strike Date:
        <ul>
            <li>The observation and strike dates are the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>There will be three observation dates and one final strike date. All of them will be determined prior to the Product Begin Date. </li>
            <li>The underlying poll lead must be higher than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the observation or strike dates.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Actual Poll Lead% - Strike Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 4, 'Bermudan Trump Put (Strike: (1.5%)', 'The poll lead is observed on three days and the strike date, and the Call is exercised if the underlying is lower than the strike', 'BGN', 1, 0.015, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Observation & Strike Date:
        <ul>
            <li>The observation and strike dates are the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>There will be three observation dates and one final strike date. All of them will be determined prior to the Product Begin Date. </li>
            <li>The underlying poll lead must be lower than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the observation or strike dates.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Strike Lead% - Actual Poll Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
"),
('DER', 4, 'Bermudan Trump Put (Strike: (1.0%)', 'The poll lead is observed on three days and the strike date, and the Call is exercised if the underlying is lower than the strike', 'BGN', 1, 0.01, 100, 'Strike', 'Notional Amount', '2024-07-15', '2024-10-06', "
<ol>
    <li>Application:
        <ul>
            <li>By submitting an application, the customer agrees to these Terms and Conditions.</li>
            <li>When applying for the derivative, the customer may request modifications.</li>
            <li>Alex Bank will review each application and reserves the right to propose modifications, which the customer may accept or not, and to deny an application with no justification.</li>
            <li>Upon approval, Alex Bank will price the instrument. Signature to the contract constitutes agreement by the customer to disburse to Alex Bank the amount of the price on or before the Product Start Date. Failure to do so shall result in product cancellation.</li>
        </ul>
    </li>
    <li>Observation & Strike Date:
        <ul>
            <li>The observation and strike dates are the date on which the poll lead is observed to determine if the Call is exercised.</li>
            <li>There will be three observation dates and one final strike date. All of them will be determined prior to the Product Begin Date. </li>
            <li>The underlying poll lead must be lower than the strike poll lead on the strike date for the Call to be exercised.</li>
        </ul>
    </li>
    <li>Underlying:
        <p>The poll lead shall be taken from the latest available data on <a href='https://projects.fivethirtyeight.com/polls/president-general/2024/national/'>FiveThirtyEight</a>.
        </p>
    </li>
    <li>Exercise of the Call:
        <ul>
            <li>The Call will be exercised if the underlying poll lead is lower than the strike poll lead on the observation or strike dates.</li>
            <li>If the Call is exercised, the customer will be entitled to the Pay-Off amount specified (Pay-Off Amount = (Strike Lead% - Actual Poll Lead%)*Notional).</li>
        </ul>
    </li>
    <li>Payment Terms:
        <ul>
            <li>The payment will be made in BGN.</li>
            <li>The Pay-Off amount will be payable if the Call is exercised.</li>
        </ul>
    </li>
    <li>Risk Acknowledgement:
        <ul>
            <li>The customer acknowledges that the value of the underlying and the outcome on the strike date are subject to market conditions and uncertainties.</li>
            <li>The customer assumes all risks associated with this product.</li>
        </ul>
    </li>
    <li>Limitation of Liability:
        <p>Alex Bank shall not be liable for any losses or damages arising from the exercise or non-exercise of the Call, except as provided by law.</p>
    </li>
    <li>Amendments:
        <p>Alex Bank reserves the right to amend these terms and conditions at any time. Any amendments will be communicated to the customer in a timely manner.</p>
    </li>
    <li>Acceptance:
        <p>By entering into this agreement, the customer accepts and agrees to these terms and conditions.</p>
    </li>
</ol>
");


insert into product_custom_column_def (`product_id`, `column_name`, `customer_visible_yn`, `customer_populatable_yn`, `column_type`, `default_value`, `exercise_date_yn`)
values 
(5, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(5, "Strike Price (% Lead)", "Y", "N", "float", "3.0", NULL), 
(5, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Actual Poll Lead% - Strike Poll Lead%)*Notional", NULL), 
(5, "Volatility", "N", "N", "float", "0.327", NULL),
(6, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(6, "Strike Price (% Lead)", "Y", "N", "float", "3.5", NULL), 
(6, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Actual Poll Lead% - Strike Poll Lead%)*Notional", NULL), 
(6, "Volatility", "N", "N", "float", "0.327", NULL),
(7, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(7, "Strike Price (% Lead)", "Y", "N", "float", "1.5", NULL), 
(7, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Strike Poll Lead% - Actual Poll Lead%)*Notional", NULL), 
(7, "Volatility", "N", "N", "float", "0.327", NULL),
(8, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(8, "Strike Price (% Lead)", "Y", "N", "float", "1.0", NULL), 
(8, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Strike Poll Lead% - Actual Poll Lead%)*Notional", NULL), 
(8, "Volatility", "N", "N", "float", "0.327", NULL),
(9, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(9, "Strike Price (% Lead)", "Y", "N", "float", "3.0", NULL), 
(9, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Actual Poll Lead% - Strike Poll Lead%)*Notional", NULL), 
(9, "Volatility", "N", "N", "float", "0.327", NULL),
(9, "First Observation Date", "Y", "N", "date", NULL, "Y"),
(9, "Second Observation Date", "Y", "N", "date", NULL, "Y"),
(9, "Third Observation Date", "Y", "N", "date", NULL, "Y"),
(10, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(10, "Strike Price (% Lead)", "Y", "N", "float", "3.5", NULL), 
(10, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Actual Poll Lead% - Strike Poll Lead%)*Notional", NULL), 
(10, "Volatility", "N", "N", "float", "0.327", NULL),
(10, "First Observation Date", "Y", "N", "date", NULL, "Y"),
(10, "Second Observation Date", "Y", "N", "date", NULL, "Y"),
(10, "Third Observation Date", "Y", "N", "date", NULL, "Y"),
(11, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(11, "Strike Price (% Lead)", "Y", "N", "float", "1.5", NULL), 
(11, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Strike Poll Lead% - Actual Poll Lead%)*Notional", NULL), 
(11, "Volatility", "N", "N", "float", "0.327", NULL),
(11, "First Observation Date", "Y", "N", "date", NULL, "Y"),
(11, "Second Observation Date", "Y", "N", "date", NULL, "Y"),
(11, "Third Observation Date", "Y", "N", "date", NULL, "Y"),
(12, "Option Price (BGN)", "Y", "N", "float", NULL, NULL), 
(12, "Strike Price (% Lead)", "Y", "N", "float", "1.0", NULL), 
(12, "Pay-off Formula", "Y", "N", "varchar", "Payoff = (Strike Poll Lead% - Actual Poll Lead%)*Notional", NULL), 
(12, "Volatility", "N", "N", "float", "0.327", NULL),
(12, "First Observation Date", "Y", "N", "date", NULL, "Y"),
(12, "Second Observation Date", "Y", "N", "date", NULL, "Y"),
(12, "Third Observation Date", "Y", "N", "date", NULL, "Y");
