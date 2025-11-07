import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized, NavigationGuardNext } from 'vue-router'

// Lazy imports
const NotFound = () => import("@/components/NotFound.vue")
const EmailAuth = () => import("@/components/EmailAuth.vue")
const AdminLogin = () => import("@/components/AdminLogin.vue")

const Customer = () => import("@/components/CustomerPage.vue")
const CustomerLogin = () => import("@/components/customer_page_components/CustomerLogin.vue")
const CustomerRegister = () => import("@/components/customer_page_components/CustomerRegister.vue")
const CustomerDashboard = () => import("@/components/customer_page_components/CustomerDashboard.vue")
const CustomerHome = () => import("@/components/customer_page_components/dashboard_components/Home.vue")
const CustomerAddToCart = () => import("@/components/customer_page_components/dashboard_components/AddToCart.vue")
const CustomerPlaceOrder = () => import("@/components/customer_page_components/dashboard_components/PlaceOrder.vue")
const CustomerOrderLogs = () => import("@/components/customer_page_components/dashboard_components/OrderLogs.vue")
const CustomerFeedback = () => import("@/components/customer_page_components/dashboard_components/ServiceFeedback.vue")
const CustomerUserProfile = () =>  import("@/components/customer_page_components/dashboard_components/UserProfile.vue")
// Admin main pages
const AdminPage = () => import("@/components/admin_page_components/AdminPage.vue")
const AdminDashboard = () => import("@/components/admin_page_components/AdminDashboard.vue")
const ProductManagement = () => import("@/components/admin_page_components/ProductManagement.vue")
const OrderManagement = () => import("@/components/admin_page_components/OrderManagement.vue")
const UserManagement = () => import("@/components/admin_page_components/UserManagement.vue")
const ViewFeedback = () => import("@/components/admin_page_components/FeedbackView.vue")
const Approvals = () => import("@/components/admin_page_components/order_management_components/Approvals.vue")
const OrderLogs = () => import("@/components/admin_page_components/order_management_components/OrderLogs.vue")

const routes = [
  { 
    path: '/admin-login',
    name: 'admin_login', 
    component: AdminLogin,
    beforeEnter: (
      to: RouteLocationNormalized, 
      from: RouteLocationNormalized, 
      next: NavigationGuardNext
    ) => {
      const secretKey = 'my-secret-key'
      if (to.query.key === secretKey) {
        next() 
      } else {
        next({ path: '/' })
      }
    }
  },

  // Customer side
  { path: '/', name: 'customer', component: Customer },
  { path: '/email-auth', name: 'email_auth', component: EmailAuth },
  { path: '/login', name: 'customer_login', component: CustomerLogin },
  { path: '/register', name: 'customer_register', component: CustomerRegister },
  { path: '/dashboard', 
    name: 'dashboard', 
    component: CustomerDashboard,
    redirect:'/dashboard/home',
    children:[
      {path: 'home',name: 'customer home',component:CustomerHome},
      {path: 'add-to-cart', name: 'customer add to cart',component:CustomerAddToCart},
      {path: 'place-order', name: 'customer place order',component:CustomerPlaceOrder},
      {path: 'user-profile', name: 'user profile',component: CustomerUserProfile},
      {path: 'order-logs', name: 'order logs',component: CustomerOrderLogs},
      {path: 'feedback', name: 'service feedback',component: CustomerFeedback},
    ]
  
  },

  // Admin side
  {
    path: '/admin',
    name: 'admin_page',
    component: AdminPage,
    redirect:'/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'admin_dashboard', component: AdminDashboard },
      { path: 'product-management', name: 'admin_product', component: ProductManagement },

      {
        path: 'order-management',
        name: 'admin_order',
        component: OrderManagement,
        children: [
          { path: 'approvals', name: 'order_approvals', component: Approvals },
          { path: 'logs', name: 'order_logs', component: OrderLogs },
        ]
      },

      { path: 'user-management', name: 'admin_user', component: UserManagement },
      { path: 'feedback', name: 'feedback in admin', component: ViewFeedback },
    ]
  },

  // Catch all
  { path: '/:pathMatch(.*)*', name: 'not_found', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
