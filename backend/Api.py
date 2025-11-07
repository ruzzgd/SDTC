from fastapi import FastAPI
from routers import OrdersManagement, ProductManagement, UserEndpoint,EmailVerifiationEnpoint,AdminEndpoint,UserAddressEndpoint,CartsManagement
def include_routers(app: FastAPI):

    app.include_router(UserEndpoint.router)
    app.include_router(EmailVerifiationEnpoint.router)
    app.include_router(AdminEndpoint.router)
    app.include_router(ProductManagement.router)
    app.include_router(OrdersManagement.router)
    app.include_router(UserAddressEndpoint.router)
    app.include_router(CartsManagement.router)