var mix = {
	methods: {
		submitPayment() {
		    const number = this.$refs.cardNumber.value.replace(/\s/g, '');
			const orderId = location.pathname.startsWith('/payment/')
				? Number(location.pathname.replace('/payment/', '').replace('/', ''))
				: null
			this.postData(`/api/payment/${orderId}/`, {
				name: this.name,
				number: number,
				year: this.year,
				month: this.month,
				code: this.code
			})
				.then(() => {
					alert('Успешная оплата')
					this.number = ''
					this.name = ''
					this.year = ''
					this.month = ''
					this.code = ''
					location.assign('/')
				})
				.catch(() => {
					console.warn('Ошибка при оплате')
				})
		}
	},
	data() {
		return {
			number: '',
			month: '',
			year: '',
			name: '',
			code: ''
		}
	}
}