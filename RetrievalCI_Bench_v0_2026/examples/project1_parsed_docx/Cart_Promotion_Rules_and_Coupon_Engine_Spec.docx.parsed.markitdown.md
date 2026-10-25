Cart Promotion Rules and Coupon Engine Spec

*Specification for cart pricing calculations, promotion hierarchy, and coupon code stacking limitations.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-CART-SPEC-005 | **Project** | NSC-CART |
| **Owner** | M-005 | **Version** | 1.3 |
| **Updated** | 2026-06-25 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-ALL-STAFF |

# Promotion Evaluation Priority

* Promotions evaluate in strict order: Catalog Price Rules -> Item Tier Discounts -> Cart Order Coupons -> Free Shipping.
* By default, coupon codes do not stack unless explicitly configured with the 'allow\_stacking' flag by the merchant.

# Cart Expiration & Cleanup

* Anonymous carts expire after 7 days of inactivity; authenticated user carts persist for 30 days.
* Expired carts automatically surrender any temporary promotional vouchers and reserved coupon redemption counts.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Promotion Type** | **Evaluation Order** | **Stackable by Default** | **Calculation Target** |
| Catalog Rule | 1 | Yes | Line item base price |
| Item Quantity Tier | 2 | No | Eligible item subtotal |
| Cart Coupon Code | 3 | No (exclusive) | Order aggregate subtotal |
| Shipping Discount | 4 | Yes | Shipping fee quote |
